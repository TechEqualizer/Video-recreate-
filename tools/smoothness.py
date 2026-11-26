#!/usr/bin/env python3
"""Per-shot smoothness: find which shots make a cut feel jerky.

Usage: python3 tools/smoothness.py VIDEO ANALYSIS_JSON
Prints the overall jerk (same as analysis.json 'jerk') and, per shot, mean motion,
absolute jerk and relative jerk (jerk / motion). Shots with relative jerk well above
the reference's overall value are the ones to fix (pop-ons, unblurred fast moves,
springs that wobble, zooms that stop dead).
"""
import json, subprocess, sys
import numpy as np

v, aj = sys.argv[1], sys.argv[2]
cuts = json.load(open(aj))['cuts_s']
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-map", "0:v:0", "-vf", "fps=30,scale=160:90,format=gray",
                      "-f", "rawvideo", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.float32)
d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2)); t = (np.arange(len(d)) + 1) / 30
keep = np.ones(len(d), bool)
for c in cuts:
    keep &= np.abs(t - c) > 0.1
dd = d[keep]
print(f"overall jerk {np.abs(np.diff(dd)).mean() / dd.mean():.3f}  mean motion {dd.mean():.2f}\n")
print("| Shot | Start | Motion | Abs jerk | Rel jerk |\n| --- | --- | --- | --- | --- |")
b = [0] + cuts + [t[-1] + 0.04]
for i in range(len(b) - 1):
    x = d[(t > b[i] + 0.1) & (t < b[i + 1] - 0.1)]
    if len(x) > 3:
        aj_ = np.abs(np.diff(x)).mean()
        print(f"| {i + 1} | {b[i]:.2f} | {x.mean():.2f} | {aj_:.2f} | {aj_ / (x.mean() + 1e-6):.2f} |")
