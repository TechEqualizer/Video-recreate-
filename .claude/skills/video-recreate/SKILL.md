---
name: "video-recreate"
description: "Entry point for this repo. Drop in one or more reference videos, pick a brand (and optionally Dw's likeness), and produce an original video in that brand that measurably matches the references' pacing, camera, look and sound. Use whenever Dw says recreate, remake, 'make one like this', 'use these references', or drops videos into inbox/."
---

# Video Recreate

The director above the departments. `ad-engine` already knows how to make one ad from a brief and a reference. This skill adds what it lacks:

1. **Many references, one target.** Each reference is measured, assigned the dimensions it is a reference *for*, and fused into one Style DNA with numbers the build must hit.
2. **Any brand, swappable.** Brands live in `brands/<name>/` as a kit. The reference's world is translated element by element into the brand's.
3. **Dw's likeness, reusable.** His face is registered once as a Higgsfield Element or Soul and reused in every project, with consent on file.
4. **Proof, not taste.** The cut is measured against the Style DNA and the references side by side before Dw sees it.

| Step | Who does it |
| --- | --- |
| Watch / download a reference | `watch` skill, or Higgsfield `media_import_url` + `video_analysis_create` |
| Measure a video | `python3 tools/analyze_reference.py` |
| Fuse references | `python3 tools/fuse_references.py` |
| Attention benchmarks | `attention-check` |
| Script (story ads, films) | `story-film-writer` |
| Spec format, critic pass | `style-director` (steps 4 and 6; its library scoring is replaced by the references) |
| Shots, realism, gates, finish | `ad-engine` (sections 5 to 9), `higgsfield-seedance-prompt` for every prompt |
| Coded type, UI, edit | `launch-motion` / `premium-motion` / `hyperframes` |
| Frame-exact rebuild of one video | `reverse-any-video` (only when Dw wants an editable 1:1 rebuild) |
| Parity | `python3 tools/parity_check.py`, `python3 tools/side_by_side.py` |

## 0. Project folder

```
projects/<slug>/
  brief.md          intake answers, mode, roles, decisions Dw owns
  refs/             the reference files (+ <name>.analysis/ from the analyzer)
  style/            roles.md, style_dna.json/.md (fused numbers), reference.md (craft breakdown), spec.md, translation.md
  shots/            shot_list.md, keyframes, prompts
  renders/          cuts and their analyses
```

Scaffold with `bash tools/new_project.sh <slug> [video ...]` (moves files from `inbox/` when no paths are given).

## 1. Intake: one message, defaults stated

Read `brands/`, `library/styles/`, `library/feedback.md` and any attachments first. Ask only what is missing:

1. **References**: files in `inbox/`, uploads or links (1 to 6). A saved style from `library/styles/` counts as a reference.
2. **Brand**: which folder in `brands/` (or "new brand": run section 6 setup first)
3. **Likeness**: Dw on camera, AI-cast talent, or no people (default: AI-cast)
4. **Mode**: *close* (same beat structure as one reference, re-cast in the brand) or *inspired* (only the Style DNA, new story). Default: close for one reference, inspired for two or more
5. **Format**: length, aspect, channel (default: the structure reference's length and aspect)
6. **Job**: the product or message, the offer and CTA (must be true; goes in the brand's truth table)

## 2. Get every reference in, really watched

- Local file: copy to `projects/<slug>/refs/`.
- Link: `watch` downloads it (yt-dlp). YouTube blocked: Higgsfield `video_analysis_create` with `youtube_url`, or ask Dw to attach the file.
- Never describe a reference that was not actually watched or measured. Say which ones failed.
- References are for learning craft. Their footage, people, logos, music, characters and lines never enter the build.

## 3. Measure, then look

For each reference:

```bash
python3 tools/analyze_reference.py projects/<slug>/refs/*.mp4
```

This writes `analysis.json`, `contact_sheet.jpg`, `sheet_dense.jpg`, a keyframe per shot and `report.md` per reference. The numbers are free; the eyes are the work:

0. If the reference ends on a legal card, logo hold or black, trim it (`ffmpeg -i ref.mp4 -t <body_end> ref_body.mp4`), re-analyze, and fuse from the body: tails distort brightness and stillness targets.
1. Open `sheet_dense.jpg` first (it shows text builds and continuous moves the cut detector can't), then `contact_sheet.jpg` and the keyframes. A long "shot" that changes a lot is usually a continuous move (carousel, orbit) or a missed cut: look at 8 fps to tell which. Read frames either side of each cut (`ffmpeg -ss <t-0.2> -i ref.mp4 -frames:v 8 -vf fps=30,scale=360:-2 f_%02d.jpg`) to see transitions, speed ramps, flashes and type entrances.
2. Fill the empty column of `report.md` per shot: shot size and FOV, subject, camera move and speed, light (key direction, Kelvin), type on screen and how it animates, transition out.
3. Name the 2 to 4 **signature moves** per reference: the things that make it feel like itself (whip pans on the beat, macro inserts, a 1-frame white flash, giant type behind the subject, a match-cut product drop).
4. When a reference needs semantic reading (what happens, what's said) and `watch` cannot transcribe it, Higgsfield `video_analysis_create` (costs credits, ask first; short clips analyse best).

## 4. Assign roles (the intelligence)

Averaging references blindly produces mush. Decide what each reference is the reference **for**: `structure` (beat order and energy curve), `pacing` (cut rhythm), `camera` (movement, stillness, smoothness), `composition` (how much of the frame the subject fills), `look` (light, grade, saturation, warmth), `sound` (loudness, tempo, cuts on the beat).

Defaults, then show Dw one line per reference to confirm:
- One reference: all roles.
- `structure` and `pacing`: the reference closest to the target channel and length.
- `look`: the reference whose grade best fits the brand's mood in `brand.md` (compare brightness, saturation, warmth).
- `sound`: the reference with the music bed Dw likes most; if unsure, the structure reference.
- `camera`: the reference with the most signature camera moves.
- Weight 2 for the reference Dw calls his favourite.

**When the brand overrides the look** (e.g. a white reference, a dark brand), drop the `look` role. Raw `motion` lives under look because frame difference scales with brightness; the camera role uses `motion_rel` (motion / contrast), which compares fairly across looks.

**Conflicts are decisions, not averages.** If pacing references disagree on `tempo_model` (one cut-driven at 4 cuts/10 s, one flythrough at 0.5) pick one model and give only that reference the `pacing` role. Same for bright-vs-dark looks. Write the choices and why in `style/roles.md`.

```bash
python3 tools/fuse_references.py \
  projects/<slug>/refs/a.analysis/analysis.json:structure,pacing,camera:2 \
  projects/<slug>/refs/b.analysis/analysis.json:look \
  projects/<slug>/refs/c.analysis/analysis.json:sound \
  --length 15 --aspect 9:16 --out projects/<slug>/style
```

Then write `style/reference.md`: the fused craft sheet. Signature moves ranked (each tagged with its source reference), transition vocabulary, type treatment, light recipe, grade, sound design per cut. Pick at most 4 signature moves for the new video; more turns into noise.

## 5. Translate the reference world into the brand

Load `brands/<brand>/brand.md`. Write `style/translation.md`, one row per element on screen or in the mix:

| Reference element | Brand equivalent | Source |
| --- | --- | --- |
| their product / hero object | our product (real photos as refs in every shot) | `brands/<b>/assets/product/` |
| their palette | brand palette, re-mixed to the reference's brightness, saturation and warmth targets | `brand.md` palette + `style_dna` look |
| their typeface style | brand fonts at the reference's size, weight and motion | `brand.md` type |
| their talent | Dw's likeness element, or AI-cast adults per `brand.md` casting | `brands/<b>/likeness/` |
| their location | a location that fits the brand world | brand moodboard |
| their VO / lines | lines in the brand voice, same length and rhythm | `brand.md` voice |
| their claim / CTA | a claim from the brand truth table | `brand.md` truth table |
| their music | original music matching BPM, energy curve and loudness | `style_dna` sound |

In **close** mode, also map each reference shot to an edit-grid slot (`style_dna.md` edit grid), keeping its size, move and duration, with brand content. In **inspired** mode, write a new concept per `ad-engine` section 4 (or `story-film-writer`), then fill the edit grid from the energy curve.

Lock `style/spec.md` in the `style-director` step 4 format, with every number cited from `style_dna`.

## 6. Brands and likeness

**New brand:** copy `brands/_template/` to `brands/<name>/` and fill `brand.md` from what Dw gives (site, logo, product photos, past posts). Ask only for gaps. A brand Dw names but has not set up gets set up first; never invent a brand's facts.

**Likeness (Dw's or anyone's):**
1. `brands/<b>/likeness/consent.md` must say who the person is and that they agreed to AI generation of their face (and voice, separately). No consent file, no likeness. Never use a reference's talent, a celebrity or anyone pulled from the web.
2. Check `likeness.yaml` for an existing ID before creating anything.
3. Register once, reuse forever:
   - **Element** (default for video): upload 1 to 6 clear photos (front, three-quarter, profile, even light) with `media_upload` / PUT / `media_confirm`, then `elements_create` with `category: character`. Use `<<<element_id>>>` in Seedance / Kling prompts.
   - **Soul** (best identity fidelity for stills): `show_characters` `action: train` with 5 to 20 photos. Only usable with `soul_2` / `soul_cinematic`, so use it for keyframes, then animate them.
   - **Voice** (opt-in only): `create_voice` from a clean recording of the same person, consent recorded separately.
4. Write the IDs back to `likeness.yaml` so the next project skips this.
5. Hero shots with the likeness: keyframe with the likeness first, check identity at full size against the source photos, then animate as `start_image`. Reject drifted faces.

## 7. Produce

Hand off to `ad-engine` from its section 5 (realism system) and section 6 (pipeline), with the spec, translation table and edit grid as the brief. Its gates are not optional:
- **GATE 1**: shot list with credit costs and the total. Nothing is generated before Dw approves that number.
- **GATE 2**: keyframes in story order next to the matching reference keyframes.

Every Seedance prompt goes through `higgsfield-seedance-prompt`, carrying the likeness element, product references and the spec's light, grade and lens lines.

## 7a. Craft bar (Apple-grade, not template-grade)

Rhythm metrics passing is not quality. Dw's verdict on FLMLNK v7 (15/15 rhythm pass): "does not look like a 10-year Apple professional". The gaps were framing, materials, light, focus and sound. Rules:

1. **Style frames before animation (hard gate).** Design 4 to 6 hero frames at full resolution, put each next to its matched reference frame, score them, and get Dw's approval before animating anything. Never animate an unapproved look.
2. **Product = a physical object.** Software is shown on real 3D devices (`build/hero3d.html` pattern: three.js PBR device, studio HDR reflections, warm key + cool rim, contact shadow on a seamless floor, depth of field, motion blur). Flat DOM cards with drop shadows read as a slideshow.
3. **Fill the frame.** One subject per shot, cropped boldly. `subject_fill_pct` and `pct_frames_filled` are at-least targets (role `composition`).
4. **One idea per screen.** Design the UI on the device as calm, real product UI with a single hero element; no collages of loud thumbnails.
5. **Light like a set.** One motivated key, a rim to separate the object, a clean seamless ground. No generic radial glow + vignette.
6. **Blind critic per shot.** A fresh reviewer scores each shot against its matched reference frame (framing, material, light, focus, type, motion) 1 to 5; anything under 4 is rebuilt before Dw sees it.
7. **Sound is half the film.** A produced score and a designed sound on every cut and action, not a synthesized temp bed, before calling a cut finished.

## 7b. Smoothness (coded motion)

Dw's first animatic "did not feel smooth"; measured jerk was 25% above the reference. Rules for every coded build:

- **Render 60 fps with motion blur.** Average 3 sub-frames across a 180-degree shutter per output frame (`build/render.js --sub 3 --shutter 0.5`). Crisp frames with no blur strobe on any fast move.
- **Cap speeds.** Pans and drifts no faster than one screen-width per ~6 s; anything faster must be blurred and eased. Carousels move at most 3 slots per shot.
- **Ease both ends.** Entrances decelerate in, exits accelerate out (sine or cubic in-out). Never start a move at full speed (no expo-out from zero on long travels).
- **Damped springs.** ~3% overshoot (k=9, w=8 in `index.html`); no visible wobble.
- **No pop-ons.** Nothing appears or disappears in one frame: every entrance fades over 0.12 to 0.2 s while it moves. Single-frame appearances were the biggest jerk source in the FLMLNK build.
- **Pushes are steady.** A punch-in or push runs the whole shot at constant or eased speed; never a fast zoom that stops dead.
- **Dark-to-bright cuts strobe more.** Keep fast motion away from the first frames after a dark/bright cut.
- **Find the culprit:** `python3 tools/smoothness.py cut.mp4 cut.analysis/analysis.json` lists jerk per shot.
- **Measure it.** `jerk` (frame-to-frame change in motion energy within shots, relative to mean motion) is in every analysis and is an at-most target in the Style DNA camera role.

## 8. Parity: prove it matches

```bash
python3 tools/analyze_reference.py projects/<slug>/renders/cut_v1.mp4 --cuts projects/<slug>/renders/cut_v1.cuts.json   # our renders know their exact cuts
python3 tools/parity_check.py projects/<slug>/style/style_dna.json projects/<slug>/renders/cut_v1.analysis/analysis.json
python3 tools/side_by_side.py projects/<slug>/refs/a.analysis/contact_sheet.jpg projects/<slug>/renders/cut_v1.analysis/contact_sheet.jpg projects/<slug>/renders/parity_v1.jpg
```

1. Every FAIL goes back with a specific fix (cut faster in slices 1 to 3, add a camera move to shots 4 and 7, lift exposure, re-time cuts to the beat). Re-run until it passes, or tell Dw which number is still off and why.
2. A fresh-eyes reviewer (the `style-director` critic pass) looks at the side-by-side and names every place the cut looks cheaper than the references, and checks every signature move in `reference.md` is present.
3. `attention-check` benchmarks. Then `ad-engine` deliverables (master, three hook variants, captions).

Never call the cut "matching" unless the parity check passed.

## 9. Learn

- After delivery, offer to save the Style DNA as `library/styles/<name>/` (copy `style_dna.json`, `reference.md`, `roles.md`, a contact sheet). Next time "make it like <name>" skips steps 2 to 4.
- Every reaction from Dw becomes a dated line in `library/feedback.md`, read at the start of every project.
- Log the project in `library/log.md`: references, roles, brand, mode, parity result, Dw's rating.

## 10. Rules

- Craft is learnable; content is not copyable. No reference footage, music, characters, logos, scripts or real people in the output. Close mode copies structure and camera language, never a protected look-alike (a famous ad's exact shots with the brand swapped is still a copy: change locations, staging and lines).
- No other brand's identity, no real person's likeness without consent on file.
- Every claim traces to the brand's truth table.
- Do everything free first (measure, fuse, translate, script, shot list, cost quote) and stop at GATE 1 when Dw is away.
- Flag where platforms require an AI-generated label; the choice is Dw's.
