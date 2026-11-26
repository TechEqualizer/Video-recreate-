# Video Recreate

Turn any reference videos into an original video for your brand, with your likeness, matched to the references by measurement rather than by eye.

```
inbox/ref1.mp4 ref2.mp4 ref3.mp4
        │  analyze_reference.py      measure every reference (cuts, motion, camera, look, sound)
        ▼
  per-reference analysis + contact sheets + shot breakdown
        │  assign roles              ref1 = structure+pacing, ref2 = look, ref3 = sound
        │  fuse_references.py
        ▼
  Style DNA  (targets with tolerances, energy curve, edit grid)
        │  translate to brand        brands/<name>/brand.md + likeness
        ▼
  spec → script → shot list → GATE 1 (credits) → keyframes → GATE 2 → Higgsfield footage → edit in code → sound
        │  parity_check.py + side_by_side.py + critic pass
        ▼
  finished cut that passes the Style DNA, plus hook variants
```

## Use it (in Claude Code)

1. Drop reference videos into `inbox/` (or paste links).
2. Set up a brand once: copy `brands/_template/` to `brands/<your-brand>/` and fill `brand.md`; add product photos, logo, fonts. For your likeness, add photos to `likeness/photos/` and fill `likeness/consent.md`.
3. Say: *"Recreate these for <brand>, 15 s vertical, me on camera."*

Claude measures and fuses the references, shows the roles and the plan, and stops for your approval before spending any credits.

## Tools (run them yourself too)

```bash
pip install -r tools/requirements.txt          # needs ffmpeg on PATH
python3 tools/analyze_reference.py inbox/*.mp4
python3 tools/fuse_references.py inbox/a.analysis/analysis.json:structure,pacing:2 inbox/b.analysis/analysis.json:look --length 15 --out projects/test/style
python3 tools/parity_check.py projects/test/style/style_dna.json renders/cut.analysis/analysis.json
```
