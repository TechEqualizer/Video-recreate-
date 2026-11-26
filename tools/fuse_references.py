#!/usr/bin/env python3
"""Fuse several reference analyses into one Style DNA: the numbers a new video must hit.

Each reference can be assigned the dimensions it is a reference FOR. One ad may be
the pacing reference, another the look/grade reference, a third the sound reference.

Usage:
    python3 tools/fuse_references.py REF [REF ...] --out projects/<p>/style [--length 15] [--aspect 9:16]

    REF = path/to/analysis.json[:roles][:weight]
          roles  = comma list of: structure, pacing, camera, look, sound  (default: all)
          weight = number (default 1)

Example:
    python3 tools/fuse_references.py \
        refs/nike.analysis/analysis.json:pacing,camera,structure:2 \
        refs/aesop.analysis/analysis.json:look \
        refs/apple.analysis/analysis.json:sound \
        --length 15 --out projects/spring-drop/style

Writes style_dna.json and style_dna.md (targets, tolerances, energy curve, edit grid).
"""
import argparse, json
from pathlib import Path

import numpy as np

ROLES = ["structure", "pacing", "camera", "look", "sound"]
DIMS = {
    "pacing": ["cuts_per_10s", "median_shot_s", "mean_shot_s", "shortest_shot_s", "longest_shot_s", "first_cut_s"],
    "camera": ["pct_shots_camera_moving", "motion_rel", "pct_static", "longest_still_s", "jerk"],
    "look": ["brightness", "contrast", "saturation", "warmth", "motion"],
    "sound": ["lufs", "bpm", "cuts_on_beat_pct"],
    "structure": ["duration_s"],
}
# how far the build may drift from a target before the parity check fails it
TOL = dict(jerk=0.1, motion_rel=0.25, cuts_per_10s=0.2, median_shot_s=0.25, mean_shot_s=0.25, shortest_shot_s=0.5, longest_shot_s=0.3, first_cut_s=0.5,
           pct_shots_camera_moving=0.2, motion=0.3, pct_static=0.5, longest_still_s=0.3, brightness=0.15, contrast=0.25,
           saturation=0.25, warmth=None, lufs=None, bpm=0.1, cuts_on_beat_pct=0.25, duration_s=0.15)
ABS_TOL = dict(warmth=12, lufs=2.0)
MIN_TOL = dict(pct_static=5, longest_still_s=0.5, pct_shots_camera_moving=10, first_cut_s=0.5, motion=1.0, cuts_on_beat_pct=10)


def parse_ref(spec):
    parts = spec.split(":")
    path, roles, w = parts[0], ROLES, 1.0
    for p in parts[1:]:
        try:
            w = float(p)
        except ValueError:
            roles = [r.strip() for r in p.split(",") if r.strip()]
            bad = [r for r in roles if r not in ROLES and r != "all"]
            if bad:
                raise SystemExit(f"unknown role {bad}; use {ROLES}")
            if "all" in roles:
                roles = ROLES
    a = json.loads(Path(path).read_text())
    return dict(path=path, roles=roles, weight=w, a=a)


def value(a, key):
    if key in a.get("metrics", {}):
        return a["metrics"][key]
    if key in (a.get("audio") or {}):
        return a["audio"][key]
    return a.get(key)


def wstats(pairs):
    pairs = [(v, w) for v, w in pairs if v is not None]
    if not pairs:
        return None
    v = np.array([p[0] for p in pairs], float)
    w = np.array([p[1] for p in pairs], float)
    return dict(target=round(float((v * w).sum() / w.sum()), 3), min=round(float(v.min()), 3), max=round(float(v.max()), 3), n=len(v))


def energy_curve(a, bins=10):
    dur = a["duration_s"] or 1
    edges = np.linspace(0, dur, bins + 1)
    cuts = np.array(a.get("cuts_s") or [])
    dens = [((cuts >= edges[i]) & (cuts < edges[i + 1])).sum() / (dur / bins) * 10 for i in range(bins)]
    mot = np.zeros(bins)
    for s in a["shots"]:
        for i in range(bins):
            ov = max(0, min(s["end_s"], edges[i + 1]) - max(s["start_s"], edges[i]))
            mot[i] += ov * s["motion"]
    mot /= dur / bins
    return np.array(dens), mot


def merge_palettes(refs):
    cols, wts = [], []
    for r in refs:
        for p in r["a"]["palette"]:
            h = p["hex"].lstrip("#")
            cols.append([int(h[i:i + 2], 16) for i in (0, 2, 4)])
            wts.append(p["share"] * r["weight"])
    cols, wts = np.array(cols, float), np.array(wts)
    order = np.argsort(-wts)
    keep = []
    for i in order:  # greedy de-dup of near colours
        if all(np.linalg.norm(cols[i] - cols[j]) > 40 for j in keep):
            keep.append(i)
        if len(keep) == 6:
            break
    tot = wts[keep].sum()
    return [dict(hex="#%02x%02x%02x" % tuple(int(c) for c in cols[i]), share=round(float(wts[i] / tot), 3)) for i in keep]


def edit_grid(length, dens_curve, pacing, bpm_stats):
    """Propose shot boundaries for a video of `length` seconds following the fused rhythm."""
    lo = max(0.4, (pacing.get("shortest_shot_s") or {}).get("target", 0.5) if pacing.get("shortest_shot_s") else 0.5)
    hi = (pacing.get("longest_shot_s") or {}).get("target", 5.0) if pacing.get("longest_shot_s") else 5.0
    base = (pacing.get("cuts_per_10s") or {}).get("target", 3.0) if pacing.get("cuts_per_10s") else 3.0
    period = 60 / bpm_stats["target"] if bpm_stats else None
    curve = dens_curve / dens_curve.mean() if dens_curve.mean() > 0 else np.ones_like(dens_curve)
    t, shots = 0.0, []
    while t < length - 0.2:
        rate = max(0.3, base * curve[min(len(curve) - 1, int(t / length * len(curve)))])
        d = float(np.clip(10 / rate, lo, max(lo, hi)))
        if period:
            d = max(period, round(d / period) * period)
        d = min(d, length - t)
        shots.append(round(d, 3))
        t += d
    starts = np.cumsum([0] + shots[:-1])
    return [dict(n=i + 1, start_s=round(float(s), 2), dur_s=d) for i, (s, d) in enumerate(zip(starts, shots))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("refs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--length", type=float, help="target length of the new video in seconds")
    ap.add_argument("--aspect", help="target aspect (default: the structure reference's)")
    args = ap.parse_args()
    refs = [parse_ref(s) for s in args.refs]

    dna = dict(references=[dict(path=r["path"], file=r["a"]["file"], roles=r["roles"], weight=r["weight"],
                                duration_s=r["a"]["duration_s"], aspect=r["a"]["aspect"]) for r in refs], targets={})
    for role, keys in DIMS.items():
        rs = [r for r in refs if role in r["roles"]]
        dna["targets"][role] = {k: wstats([(value(r["a"], k), r["weight"]) for r in rs]) for k in keys}
        dna["targets"][role] = {k: v for k, v in dna["targets"][role].items() if v}
    for role, d in dna["targets"].items():
        for k, s in d.items():
            s["tolerance"] = ABS_TOL[k] if k in ABS_TOL else round(max(abs(s["target"]) * TOL[k], MIN_TOL.get(k, 0)), 3)

    srefs = [r for r in refs if "structure" in r["roles"]] or refs
    curves = [energy_curve(r["a"]) for r in srefs]
    w = np.array([r["weight"] for r in srefs])
    dens = (np.array([c[0] for c in curves]) * w[:, None]).sum(0) / w.sum()
    mot = (np.array([c[1] for c in curves]) * w[:, None]).sum(0) / w.sum()
    dna["energy_curve"] = dict(bins="10 equal slices of runtime", cut_density_per_10s=[round(float(x), 2) for x in dens],
                               motion=[round(float(x), 2) for x in mot])
    tempo = [r["a"]["metrics"]["tempo_model"] for r in refs if "pacing" in r["roles"]] or [refs[0]["a"]["metrics"]["tempo_model"]]
    dna["tempo_model"] = max(set(tempo), key=tempo.count)
    lrefs = [r for r in refs if "look" in r["roles"]] or refs
    dna["palette_mood"] = merge_palettes(lrefs)
    dna["aspect"] = args.aspect or srefs[0]["a"]["aspect"]
    length = args.length or dna["targets"]["structure"].get("duration_s", {}).get("target")
    dna["length_s"] = length
    if args.length:  # the new video's length is a decision, not something inherited from the refs
        t = dna["targets"]["structure"]
        t["duration_s"] = dict(target=args.length, min=args.length, max=args.length, n=0, tolerance=round(args.length * 0.05, 2))
    if length:
        dna["edit_grid"] = edit_grid(length, dens, dna["targets"]["pacing"], dna["targets"]["sound"].get("bpm"))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "style_dna.json").write_text(json.dumps(dna, indent=1))
    (out / "style_dna.md").write_text(to_md(dna))
    print(f"wrote {out/'style_dna.json'} and {out/'style_dna.md'}")


def to_md(d):
    L = ["# Style DNA", "", "Fused from:", ""]
    for r in d["references"]:
        L.append(f"- `{Path(r['file']).name}` ({r['duration_s']} s, {r['aspect']}): reference for **{', '.join(r['roles'])}**, weight {r['weight']}")
    L += ["", f"Target: **{d['length_s']} s, {d['aspect']}**, tempo model **{d['tempo_model']}**", "",
          "## Targets the build must hit", "", "| Dimension | Metric | Target | Tolerance | Range across refs |", "| --- | --- | --- | --- | --- |"]
    for role, ks in d["targets"].items():
        for k, s in ks.items():
            L.append(f"| {role} | {k} | {s['target']} | ±{s['tolerance']} | {s['min']} to {s['max']} (n={s['n']}) |")
    L += ["", "## Energy curve (10 slices of runtime)", "", "| Slice | " + " | ".join(str(i + 1) for i in range(10)) + " |",
          "| --- |" + " --- |" * 10,
          "| Cuts / 10 s | " + " | ".join(str(x) for x in d["energy_curve"]["cut_density_per_10s"]) + " |",
          "| Motion | " + " | ".join(str(x) for x in d["energy_curve"]["motion"]) + " |", "",
          "Palette mood (from the look references; the brand palette replaces it, this sets value, saturation and warmth): "
          + " ".join(f"`{p['hex']}`" for p in d["palette_mood"]), ""]
    if d.get("edit_grid"):
        L += ["## Edit grid (proposed shot slots)", "", "| Slot | Start | Duration | Beat (fill) | Content (fill) |", "| --- | --- | --- | --- | --- |"]
        for s in d["edit_grid"]:
            L.append(f"| {s['n']} | {s['start_s']} | {s['dur_s']} | | |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
