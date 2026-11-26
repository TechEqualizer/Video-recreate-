# Video Recreate

Dw's reference-to-brand video system: drop in reference videos, pick a brand (and optionally his likeness), get an original video in that brand that measurably matches the references.

## Start here
- Any "recreate / remake / make one like this / here are my references" request: load the `video-recreate` skill (`.claude/skills/video-recreate/SKILL.md`). It runs the other skills in order.
- New reference files land in `inbox/`. `bash tools/new_project.sh <slug>` moves them into a project.

## Layout
- `.claude/skills/`: the video skills (video-recreate is the entry point; ad-engine, style-director, story-film-writer, launch-motion, premium-motion, attention-check, higgsfield-seedance-prompt, reverse-any-video, watch, hyperframes, printful-tee-mockups). This repo is now their source of truth; edit them here.
- `tools/`: free, offline measurement (Python 3 + ffmpeg + numpy + Pillow)
  - `analyze_reference.py VIDEO...`: cuts, shot list, motion, camera movement, stillness, brightness, saturation, warmth, palette, LUFS, BPM, cuts-on-beat, contact sheet
  - `fuse_references.py REF:roles:weight ... --length --aspect --out`: Style DNA targets, energy curve, edit grid
  - `parity_check.py style_dna.json cut.analysis.json`: PASS/FAIL per target (exit 1 on any fail)
  - `side_by_side.py`: reference vs. cut contact sheets
- `brands/<name>/`: brand kit (`brand.md` with truth table, assets, `likeness/` with consent and saved Higgsfield IDs). `_template/` to start a new one.
- `library/`: saved styles, feedback rules, project log. Read `library/feedback.md` at the start of every project.
- `projects/<slug>/`: one per video.

## Rules
- Never spend Higgsfield credits without Dw's yes to the exact total (ad-engine GATE 1).
- Borrow the references' craft, never their footage, music, people, logos or lines.
- A likeness needs `likeness/consent.md` filled in. Never a reference's talent or anyone from the web.
- Every on-screen claim comes from the brand's truth table.
- Don't call a cut "matching" unless `parity_check.py` passed.
