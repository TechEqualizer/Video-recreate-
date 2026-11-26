---
name: "attention-check"
description: "Measure any video (a reference or our own cut) for cut rate, motion, stillness, brightness and loudness, and compare it to attention benchmarks before delivery."
---

# Attention Check

Taste is judged by eye, but attention can be measured. Run this on every reference Dw sends and on every cut before he sees it. A cut that fails a benchmark goes back for revision, and the report says which numbers moved.

## The measurement script

Save as `analyze.py` and run `python3 analyze.py video.mp4 [more.mp4 ...]` (needs ffmpeg and numpy; works in the Claude workspace or the Higgsfield sandbox).

```python
import subprocess, json, re, sys, numpy as np
def run(v):
    dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",v]))
    err = subprocess.run(["ffmpeg","-v","info","-i",v,"-map","0:v:0","-vf","scale=320:-2,select='gt(scene,0.28)',showinfo","-an","-f","null","-"],capture_output=True,text=True).stderr
    cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", err)]
    raw = subprocess.run(["ffmpeg","-v","error","-i",v,"-map","0:v:0","-vf","fps=6,scale=96:54,format=gray","-f","rawvideo","-"],capture_output=True).stdout
    a = np.frombuffer(raw,np.uint8).reshape(-1,54,96).astype(np.float32)
    d = np.abs(np.diff(a,axis=0)).mean(axis=(1,2))
    au = subprocess.run(["ffmpeg","-v","info","-i",v,"-map","0:a:0","-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
    I = re.findall(r"I:\s*(-?[\d.]+) LUFS", au)
    shots = np.diff([0]+cuts+[dur])
    still_runs, run_len = [], 0
    for x in d:
        run_len = run_len + 1 if x < 0.6 else 0
        still_runs.append(run_len)
    return dict(file=v, dur=round(dur,1), cuts_per_10s=round(len(cuts)/dur*10,1), median_shot_s=round(float(np.median(shots)),2),
                motion=round(float(d.mean()),2), pct_static=round(float((d<0.6).mean()*100)),
                longest_still_s=round(max(still_runs)/6,1), brightness=round(float(a.mean())), first_cut_s=round(cuts[0],2) if cuts else None,
                motion_by_quarter=[round(float(q.mean()),2) for q in np.array_split(d,4)], LUFS=I[-1] if I else None)
for v in sys.argv[1:]:
    print(json.dumps(run(v)))
```

## Benchmarks (from Dw's reference set: Apple iPhone 18 Pro, Apple HomeView, Artlist x Claude, Higgsfield Katana, Membrain, Madison, FCS)

| Metric | Reference range | Our target | Our FLMLNK v3 (failed) |
| --- | --- | --- | --- |
| Static frames (pct_static) | 1 to 38%, median 18% | 20% or less | 59% |
| Longest still stretch | under 2 s | 1.5 s or less | several seconds |
| Motion (mean frame difference) | 5.3 to 15.3 | 5 or more | 1.6 |
| Brightness (0 to 255) | 46 to 227 | 45 or more; dark styles need colour glows | 23 |
| Tempo | Either 2.5+ cuts per 10 s (cut-driven) or under 1 cut per 10 s with a camera that never stops (flythrough) | Pick one model in the Style Spec | 0 cuts, slow fades |
| Length | 35 to 70 s typical; longer only with 6+ cuts per 10 s or nonstop UI | 60 to 90 s for a first touch | 3:32 |
| Energy shape | Motion highest in the first quarter or rising into the reveal | First quarter at or above the average | flat |
| Loudness | -7 (social) to -19 LUFS | -14 social, -16 web | -16 |

## How to use it

1. **References:** run the script on every reference Dw sends, plus contact sheets (one frame every 3 to 4 percent of the runtime, timestamped). Record the numbers and observations in the `style-director` library row for that style.
2. **Before delivery:** run it on the cut. Any metric outside the target goes back to production with a specific fix (add a camera move, cut faster, lift exposure, shorten). Re-run until it passes or tell Dw which number is still off and why.
3. **In the report to Dw:** one line per metric, ours against the reference range.