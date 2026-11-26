#!/usr/bin/env python3
"""Compare our cut against the Style DNA. Exit code 1 if any target fails.

Usage:
    python3 tools/analyze_reference.py projects/<p>/renders/cut_v1.mp4
    python3 tools/parity_check.py projects/<p>/style/style_dna.json projects/<p>/renders/cut_v1.analysis/analysis.json
"""
import json, sys

AT_LEAST = {"cuts_on_beat_pct"}  # more is better
AT_MOST = {"pct_static", "longest_still_s", "jerk"}  # less is better
from pathlib import Path


def main(dna_p, cut_p):
    dna, cut = json.loads(Path(dna_p).read_text()), json.loads(Path(cut_p).read_text())
    rows, fails = [], 0
    for role, ks in dna["targets"].items():
        for k, s in ks.items():
            v = cut["metrics"].get(k, (cut.get("audio") or {}).get(k, cut.get(k)))
            if v is None:
                rows.append((role, k, s["target"], s["tolerance"], "n/a", "SKIP"))
                continue
            ok = abs(v - s["target"]) <= s["tolerance"] or s["min"] <= v <= s["max"]
            if k in AT_LEAST:  # only falling short fails
                ok = v >= s["target"] - s["tolerance"]
            if k in AT_MOST:  # only going over fails
                ok = v <= s["target"] + s["tolerance"]
            fails += not ok
            rows.append((role, k, s["target"], s["tolerance"], v, "PASS" if ok else "FAIL"))
    if cut["aspect"] != dna["aspect"]:
        rows.append(("format", "aspect", dna["aspect"], "-", cut["aspect"], "FAIL")); fails += 1
    print("| Dimension | Metric | Target | Tol | Ours | Result |\n| --- | --- | --- | --- | --- | --- |")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    print(f"\n{fails} failing metric(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
