#!/usr/bin/env python3
"""Measure a reference video (or our own cut) and write a machine-readable breakdown.

Usage:
    python3 tools/analyze_reference.py VIDEO [--out DIR] [--scene 0.30] [--fps 6]

Writes into DIR (default: <video dir>/<video stem>.analysis/):
    analysis.json      every number the build and the parity check use
    contact_sheet.jpg  one keyframe per shot, timestamped
    sheet_dense.jpg    ~120 timestamped frames at a fixed rate (beats, text builds, transitions)
    shots/NNN.jpg      the keyframe of each shot (mid-point)
    report.md          a readable summary to start the shot-by-shot breakdown

Needs ffmpeg/ffprobe, numpy and Pillow. No network, no credits.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 160, 90  # analysis resolution


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, **kw)


def probe(v):
    out = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(v)], text=True).stdout
    j = json.loads(out)
    vs = next(s for s in j["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in j["streams"])
    num, den = (vs.get("avg_frame_rate") or vs.get("r_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 30.0
    w, h = int(vs["width"]), int(vs["height"])
    rot = 0
    for sd in vs.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", 0) or 0)
    if abs(rot) in (90, 270):
        w, h = h, w
    dur = float(j["format"].get("duration") or vs.get("duration") or 0)
    return dict(duration_s=round(dur, 3), fps=round(fps, 3), width=w, height=h,
                aspect=aspect_name(w, h), has_audio=has_audio)


def aspect_name(w, h):
    r = w / h
    for name, val in [("9:16", 9 / 16), ("4:5", 4 / 5), ("1:1", 1), ("16:9", 16 / 9), ("2.39:1", 2.39), ("4:3", 4 / 3)]:
        if abs(r - val) / val < 0.04:
            return name
    return f"{w}:{h}"


def detect_cuts(v, thr):
    err = sh(["ffmpeg", "-hide_banner", "-v", "info", "-i", str(v), "-map", "0:v:0", "-vf",
              f"scale=320:-2,select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-"], text=True).stderr
    cuts = sorted(float(x) for x in re.findall(r"pts_time:([\d.]+)", err))
    merged = []  # drop flicker: cuts closer than 0.25 s
    for c in cuts:
        if c > 0.1 and (not merged or c - merged[-1] > 0.25):
            merged.append(round(c, 3))
    return merged


def detect_cuts_diff(v, rate=15):
    """Second detector: isolated spikes in frame difference. Catches cuts between similar-looking
    shots (white text card -> white product shot) that ffmpeg's scene score misses, while ignoring
    steady motion and small text builds."""
    raw = sh(["ffmpeg", "-v", "error", "-i", str(v), "-map", "0:v:0", "-vf", f"fps={rate},scale=96:54,format=gray",
              "-f", "rawvideo", "-"]).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 54, 96).astype(np.float32)
    if len(a) < 3:
        return []
    d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    cuts = []
    for i in range(len(d)):
        nb = np.concatenate([d[max(0, i - 3):i], d[i + 1:i + 4]])
        base = float(np.median(nb)) if len(nb) else 0.0
        if d[i] > 4.0 and d[i] > 3 * base + 1.5:
            cuts.append(round((i + 1) / rate, 3))
    return cuts


def merge_cuts(*lists, gap=0.25):
    out = []
    for c in sorted(x for l in lists for x in l):
        if c > 0.1 and (not out or c - out[-1] > gap):
            out.append(c)
    return out


def jerkiness(v, cuts, rate=30):
    """Smoothness: how abruptly motion energy changes from frame to frame inside shots
    (cuts excluded), relative to the average motion. Lower = smoother. Strobing pans,
    wobbling springs and frame-rate judder all raise it."""
    raw = sh(["ffmpeg", "-v", "error", "-i", str(v), "-map", "0:v:0", "-vf", f"fps={rate},scale=160:90,format=gray",
              "-f", "rawvideo", "-"]).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.float32)
    if len(a) < 4:
        return None
    d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    t = (np.arange(len(d)) + 1) / rate
    keep = np.ones(len(d), bool)
    for c in cuts:
        keep &= np.abs(t - c) > 0.1
    d = d[keep]
    return round(float(np.abs(np.diff(d)).mean() / (d.mean() + 1e-6)), 3)


def subject_fill(frames):
    """Share of the frame the subject occupies: pixels that differ clearly from the background
    (median of the frame border). Works for light and dark grounds. Apple-style product films
    fill the frame; floating small objects in a void read as amateur."""
    g = frames.mean(-1)
    border = np.concatenate([g[:, :6].reshape(len(g), -1), g[:, -6:].reshape(len(g), -1),
                             g[:, :, :4].reshape(len(g), -1), g[:, :, -4:].reshape(len(g), -1)], 1)
    bg = np.median(border, 1)[:, None, None]
    f = (np.abs(g - bg) > 22).mean(axis=(1, 2))
    return round(float(np.median(f) * 100), 1), round(float((f > 0.35).mean() * 100), 1)


def decode_frames(v, fps):
    raw = sh(["ffmpeg", "-v", "error", "-i", str(v), "-map", "0:v:0", "-vf", f"fps={fps},scale={W}:{H}",
              "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32)


def phase_shift(a, b):
    """Global translation between two gray frames (pixels), via phase correlation."""
    fa, fb = np.fft.fft2(a), np.fft.fft2(b)
    r = fa * np.conj(fb)
    r /= np.abs(r) + 1e-6
    c = np.abs(np.fft.ifft2(r))
    y, x = np.unravel_index(np.argmax(c), c.shape)
    if y > H // 2: y -= H
    if x > W // 2: x -= W
    return float(np.hypot(x, y))


def kmeans_palette(px, k=6, iters=12, seed=0):
    rng = np.random.default_rng(seed)
    if len(px) > 20000:
        px = px[rng.choice(len(px), 20000, replace=False)]
    cent = px[rng.choice(len(px), k, replace=False)]
    for _ in range(iters):
        lab = np.argmin(((px[:, None] - cent[None]) ** 2).sum(-1), 1)
        for i in range(k):
            m = px[lab == i]
            if len(m):
                cent[i] = m.mean(0)
    share = np.bincount(lab, minlength=k) / len(lab)
    order = np.argsort(-share)
    return [dict(hex="#%02x%02x%02x" % tuple(int(c) for c in cent[i]), share=round(float(share[i]), 3)) for i in order]


def color_stats(fr):
    r, g, b = fr[..., 0], fr[..., 1], fr[..., 2]
    mx, mn = fr.max(-1), fr.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return dict(brightness=round(float(luma.mean()), 1), contrast=round(float(luma.std()), 1),
                saturation=round(float(sat.mean()), 3), warmth=round(float((r - b).mean()), 1))


def audio_analysis(v, dur, cuts):
    res = dict(lufs=None, bpm=None, cuts_on_beat_pct=None)
    err = sh(["ffmpeg", "-hide_banner", "-v", "info", "-i", str(v), "-map", "0:a:0", "-af", "ebur128", "-f", "null", "-"], text=True).stderr
    I = re.findall(r"I:\s*(-?[\d.]+) LUFS", err)
    res["lufs"] = float(I[-1]) if I else None
    sr, hop = 11025, 128
    raw = sh(["ffmpeg", "-v", "error", "-i", str(v), "-map", "0:a:0", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]).stdout
    x = np.frombuffer(raw, np.float32)
    if len(x) < sr * 3:
        return res
    n = len(x) // hop
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    env = np.concatenate([[0], np.maximum(np.diff(np.log(rms + 1e-4)), 0)])
    env -= env.mean()
    fr = sr / hop  # envelope frames per second
    ac = np.correlate(env, env, "full")[len(env) - 1:]
    lo, hi = int(fr * 60 / 180), int(fr * 60 / 70)
    if hi + 1 >= len(ac):
        return res
    k = lo + int(np.argmax(ac[lo:hi]))
    h = k // 2  # octave check: a strong peak at half the lag means we found every other beat
    if h - 1 >= lo and ac[h - 1:h + 2].max() > 0.6 * ac[k]:
        k = h - 1 + int(np.argmax(ac[h - 1:h + 2]))
    a0, a1, a2 = ac[k - 1], ac[k], ac[k + 1]  # parabolic refinement of the peak
    den = a0 - 2 * a1 + a2
    lag = k + (0.5 * (a0 - a2) / den if den else 0)
    bpm = 60 * fr / lag
    period = lag / fr
    t = np.arange(len(env)) / fr
    best, t0 = -np.inf, 0.0
    for ph in np.arange(0, period, 1 / fr):  # phase with the most onset energy on the grid
        grid = np.arange(ph, t[-1], period)
        sc = np.interp(grid, t, env).sum()
        if sc > best:
            best, t0 = sc, ph
    res["bpm"] = round(float(bpm), 1)
    res["beat_period_s"] = round(float(period), 3)
    res["beat_phase_s"] = round(float(t0 % period), 3)
    if cuts:
        tol = min(0.08, period / 4)
        on = [abs(((c - t0 + period / 2) % period) - period / 2) <= tol for c in cuts]
        res["cuts_on_beat_pct"] = round(100 * sum(on) / len(on))
    return res


def keyframe(v, t, path):
    sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(v), "-frames:v", "1", "-vf", "scale=360:-2", str(path)])


def contact_sheet(paths, labels, out, cols=6):
    ims = [Image.open(p).convert("RGB") for p in paths if Path(p).exists()]
    if not ims:
        return
    tw = 360
    th = int(ims[0].height * tw / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), "black")
    d = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(im.resize((tw, th)), (x, y))
        d.text((x + 6, y + th + 4), lab, fill="white")
    sheet.save(out, quality=88)


def analyze(v, out, thr, fps, known_cuts=None):
    v = Path(v)
    out.mkdir(parents=True, exist_ok=True)
    (out / "shots").mkdir(exist_ok=True)
    meta = probe(v)
    dur = meta["duration_s"]
    # our own renders know their exact cuts; references are detected
    cuts = [round(c, 3) for c in known_cuts] if known_cuts else merge_cuts(detect_cuts(v, thr), detect_cuts_diff(v))
    frames = decode_frames(v, fps)
    gray = frames.mean(-1)
    diff = np.abs(np.diff(gray, axis=0)).mean(axis=(1, 2)) if len(gray) > 1 else np.zeros(1)
    shifts = np.array([phase_shift(gray[i], gray[i + 1]) for i in range(len(gray) - 1)]) if len(gray) > 1 else np.zeros(1)

    bounds = [0.0] + cuts + [dur]
    shots = []
    for i in range(len(bounds) - 1):
        s, e = bounds[i], bounds[i + 1]
        a, b = int(s * fps), max(int(s * fps) + 1, int(e * fps))
        fr = frames[a:b] if b <= len(frames) else frames[a:]
        if len(fr) == 0:
            fr = frames[-1:]
        d_in = diff[a:max(a + 1, b - 1)] if len(diff) else np.zeros(1)
        sh_in = shifts[a:max(a + 1, b - 1)] if len(shifts) else np.zeros(1)
        cam = float(np.median(sh_in)) if len(sh_in) else 0.0
        mot = float(d_in.mean()) if len(d_in) else 0.0
        kf = out / "shots" / f"{i + 1:03d}.jpg"
        keyframe(v, (s + e) / 2, kf)
        shots.append(dict(n=i + 1, start_s=round(s, 3), end_s=round(e, 3), dur_s=round(e - s, 3),
                          motion=round(mot, 2), camera_shift_px=round(cam, 2),
                          camera="moving" if cam >= 0.5 else ("subject-motion" if mot >= 3 else "locked"),
                          palette=kmeans_palette(fr.reshape(-1, 3), k=3), **color_stats(fr), keyframe=str(kf.relative_to(out))))

    durs = np.array([s["dur_s"] for s in shots])
    still = run = 0
    for x in diff:
        run = run + 1 if x < 0.6 else 0
        still = max(still, run)
    q = np.array_split(diff, 4)
    m = dict(
        shot_count=len(shots),
        cuts_per_10s=round(len(cuts) / dur * 10, 2) if dur else 0,
        median_shot_s=round(float(np.median(durs)), 2),
        mean_shot_s=round(float(durs.mean()), 2),
        shortest_shot_s=round(float(durs.min()), 2),
        longest_shot_s=round(float(durs.max()), 2),
        first_cut_s=cuts[0] if cuts else None,
        motion=round(float(diff.mean()), 2),
        pct_static=round(float((diff < 0.6).mean() * 100)),
        longest_still_s=round(still / fps, 2),
        pct_shots_camera_moving=round(100 * sum(s["camera"] == "moving" for s in shots) / len(shots)),
        motion_by_quarter=[round(float(x.mean()), 2) if len(x) else 0 for x in q],
        **color_stats(frames),
    )
    m["jerk"] = jerkiness(v, cuts)
    m["subject_fill_pct"], m["pct_frames_filled"] = subject_fill(frames)
    # motion relative to contrast: comparable across bright and dark looks
    m["motion_rel"] = round(m["motion"] / m["contrast"], 3) if m["contrast"] else None
    m["energy_shape"] = ("front-loaded" if m["motion_by_quarter"][0] >= max(m["motion_by_quarter"]) * 0.9 else
                         "rising" if m["motion_by_quarter"][-1] >= max(m["motion_by_quarter"]) * 0.9 else "mid-peak")
    m["tempo_model"] = "cut-driven" if m["cuts_per_10s"] >= 2.5 else ("flythrough" if m["pct_shots_camera_moving"] >= 60 else "slow")
    audio = audio_analysis(v, dur, cuts) if meta["has_audio"] else {}

    result = dict(file=str(v), **meta, metrics=m, audio=audio,
                  palette=kmeans_palette(frames.reshape(-1, 3), k=6), cuts_s=cuts, shots=shots)
    (out / "analysis.json").write_text(json.dumps(result, indent=1))
    contact_sheet([out / s["keyframe"] for s in shots],
                  [f'#{s["n"]} {s["start_s"]:.2f}s ({s["dur_s"]:.1f}s) {s["camera"]}' for s in shots],
                  out / "contact_sheet.jpg")
    dense_sheet(v, dur, out / "sheet_dense.jpg")
    write_report(result, out / "report.md")
    return result


def dense_sheet(v, dur, path, frames=120, cols=12):
    """Timestamped frames at a fixed rate (~120 for the whole video): the best single view of beats,
    text builds and transitions that one-keyframe-per-shot misses."""
    rate = max(0.5, min(4.0, frames / max(dur, 1)))
    rows = int(np.ceil(dur * rate / cols))
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-vf",
        f"fps={rate},scale=240:-2,drawtext=text='%{{pts\\:hms}}':x=4:y=4:fontsize=14:fontcolor=red:box=1,tile={cols}x{rows}",
        "-frames:v", "1", str(path)])


def write_report(r, path):
    m, a = r["metrics"], r.get("audio") or {}
    L = [f"# Reference breakdown: {Path(r['file']).name}", "",
         f"{r['width']}x{r['height']} ({r['aspect']}), {r['fps']} fps, {r['duration_s']} s, audio: {r['has_audio']}", "",
         "## Measured", "", "| Metric | Value |", "| --- | --- |"]
    for k, val in m.items():
        L.append(f"| {k} | {val} |")
    for k, val in a.items():
        L.append(f"| audio.{k} | {val} |")
    L += ["", "Palette: " + " ".join(f"`{p['hex']}` {int(p['share'] * 100)}%" for p in r["palette"]), "",
          "## Shots", "", "| # | Start | Dur | Camera | Motion | Bright | Warmth | Colours | Shot size / subject / move / light / type on screen (fill by eye) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in r["shots"]:
        L.append(f"| {s['n']} | {s['start_s']:.2f} | {s['dur_s']:.2f} | {s['camera']} | {s['motion']} | {s['brightness']} | {s['warmth']} | "
                 + " ".join(p["hex"] for p in s["palette"]) + " | |")
    L += ["", "## Signature moves (fill by eye from contact_sheet.jpg and frame-by-frame looks)", "", "1. ", "2. ", "3. "]
    path.write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video", nargs="+")
    ap.add_argument("--out", help="output dir (only with a single video)")
    ap.add_argument("--scene", type=float, default=0.30, help="ffmpeg scene-change threshold")
    ap.add_argument("--fps", type=float, default=6, help="analysis sample rate")
    ap.add_argument("--cuts", help="exact cut times for our own renders: 'a,b,c' or a JSON file with a 'cuts' list")
    args = ap.parse_args()
    for v in args.video:
        out = Path(args.out) if args.out and len(args.video) == 1 else Path(v).with_suffix("").with_name(Path(v).stem + ".analysis")
        kc = None
        if args.cuts:
            kc = json.load(open(args.cuts))["cuts"] if args.cuts.endswith(".json") else [float(x) for x in args.cuts.split(",")]
        r = analyze(v, out, args.scene, args.fps, kc)
        print(json.dumps(dict(file=v, out=str(out), **r["metrics"], audio=r.get("audio")), separators=(",", ":")))
