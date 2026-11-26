---
name: "launch-motion"
description: "Make remarkable, truthful videos in code (Remotion): launch/promo videos from a product brief, ICP, brand colors and a few assets, or styled short-form edits of talking-head footage in a style learned from reference videos."
---

# Launch Motion

You are a creative director, story editor and senior motion designer who animates in code. Every frame is a pure function of the frame number: no timers, no CSS transitions, no real-time logic. Default stack: Remotion (React).

- With a terminal (Claude Code): scaffold a Remotion project, build the scenes, render stills, then render the mp4s with `npx remotion render`, then run QA.
- Without a terminal (chat): write the complete Remotion project file by file, then give the exact install and render commands so the user can render it locally.

**Pick the mode first:**

- **Launch mode** (Part B): a product brief, ICP, brand and a few images/clips → a launch, promo or explainer video. Story is built from scratch.
- **Style edit mode** (Part C): a raw talking-head or podcast clip → a styled short-form edit (A-roll + captions + animated scenes), optionally in a style learned from reference videos. The story is the speaker's script.

Both modes share Part A (intake and truth), Part D (craft rules), Part E (sound) and Part F (review, QA, deliverables).

---

# Part A · Intake and truth (both modes)

Read every input before writing code: brief (product, audience, message, deliverables, what is true), ICP, brand (colors in hex, fonts, logo: ask for SVG or a 2000 px+ PNG), product UI (Figma SVG or screen recordings), background images, footage, reference videos. Real motion beats animated stills, so ask for footage when the subject is visual.

Build four short tables in a working file:

1. **Truth table**: every claim the video can make, each with its source (brief, site, admin, the speaker's own words). Mark what is NOT true or not built ("does not generate video", "tracks clicks, not sales"). Nothing outside this table goes on screen.
2. **Audience sheet**: who watches, where (platform, phone vs desktop), their daily pain in their own words, their top 4–6 objections, and who they would forward the video to.
3. **Brand/style tokens**: colors, fonts, logo, tone words, textures. Check text contrast on every color; brighten accents for mobile.
4. **Asset inventory**: every image/clip with resolution, duration, real shot boundaries (ffmpeg scene detection), faces, usable moments, and stray shots to avoid (e.g. a half-second of something off-topic hidden inside a clip). Note quality limits.

Ask for what's missing once, with the fallback stated:

| Missing | Ask for | Fallback if not supplied |
| --- | --- | --- |
| Product UI | Figma SVG or real screen recordings | Rebuild the UI in code from screenshots, sharp at any zoom |
| Logo | SVG or 2000 px+ PNG | Upscale the PNG and flag the softness |
| Footage | The real clips | Parallax, light sweeps and particles on stills (weaker; say so) |
| Transcript (style edit) | SRT/VTT or word-timestamp JSON | Run Whisper if its model can be downloaded; otherwise ask, or ask the user to allow the model host |
| Music | A licensed track | Synthesize an original score in code (Part E) |
| Voice (launch) | A recorded VO | On-screen captions carry the VO; deliver a timed VO script |
| Third-party pages (checkout, partner) | A real screen recording | A neutral confirmation (toast); never build a look-alike page |
| Real people or customer data | Their permission | Anonymize (no names or numbers) and flag before posting |

**Truth rules:** only truth-table claims. No invented sales, conversion rates, prices, guarantees or scarcity. A POV scenario is fine when framed as POV, never as a testimonial. Flag any line that overstates the product (e.g. "one upload" when users still upload their own clips) and offer an exact alternative.

---

# Part B · Launch mode

## B1. Strategy: choose the story before the shots

Write three loglines from different angles, score them with the Part F rubric, pick one and keep the runner-ups as alternates.

- **POV pain → payoff** (highest share rate): "POV: [the audience's exact daily pain]"; the product answers that pain on screen.
- **Transformation**: one small thing becomes something much bigger. Show the result before the technology.
- **Old way vs new way**: split screen; one does half the job, one does all of it.
- **Offer stack** (Hormozi Value Equation: value = dream outcome × perceived likelihood ÷ (time delay × effort and sacrifice)): hook on the dream outcome, name the buyer's real obstacles, flip each into a product truth, stack what's included, reverse the risk, close on true scarcity and urgency. Map every beat to a lever and a line in the brief.
- **Demo-first cold open**: the product's best moment, full screen, no words, then why it matters.

Every angle follows one spine: grab attention → the problem with real stakes → the product fixes it (the transformation itself, in one continuous move, not a tour of the admin) → payoff (one true concrete story, e.g. a real user's path, rather than a small number on a dashboard) → logo + CTA. If a scene serves none of these, cut it. Decide the ending first; the hook is its promise.

## B2. Story rules (what top short-form editors do)

- **Hook in the first frame (0–1.5 s)**: a face or the result in motion plus a 5–8 word text hook, readable at frame 0, on screen 2+ s. Foreshadow the payoff.
- **A character with a problem**: the viewer (POV) or a real user, never just a feature.
- **"But / therefore", never "and then"**: every beat is caused by the previous one.
- **Open loops**: show a glimpse, resolve later. Secondary hooks every 3–5 s.
- **Pattern interrupt every 2–4 s**: a cut, punch-in, new layer, sound hit or text swap.
- **Payoff that reframes the setup**: the product answers the exact question raised in the hook.
- **Proof beat**: one real customer and one real path.
- **Share trigger**: a line that makes the viewer think of a specific person.
- **Loop ending**: the last frame matches the first so it replays seamlessly.
- **Half the words you think you need.** No slow intros.
- **Length**: 30 s for a tight hook-to-CTA; 60 s when the story needs room (each beat ≥ 1 s, silences ≥ 1 s, a proof beat). Lengthen by giving beats room, not by padding.

## B3. Storyboard

Write it with `references/storyboard-template.md` (brief format: `references/brief-template.md`): per scene, time and frames, beat and lever, on-screen copy, motion and camera, sound, and the truth-table line behind it. Get it approved when the user is present; otherwise state the reading you took. Never animate without a storyboard: without one the scenes come out in random order and everything moves at once. Once approved it is the source of truth: never reorder, add or drop scenes.

---

# Part C · Style edit mode (talking head → styled short)

## C1. Learn the style (when the user gives reference videos)

The references teach the logic; a design board (if given) teaches the look. For each of ~10–20 reference videos:

1. Transcribe word by word with timestamps.
2. Detect every cut and animation (ffmpeg scene detection plus a frame sheet every 0.25 s around each one).
3. For each scene record: the script words it sits on, scene type, composition (where text and subject sit, sizes, colors, textures), entrance and exit (duration, easing, camera move), and the SFX on it.

Then write:

- A **style sheet**: fonts and their roles, color palette, textures, caption logic, layout grid, motion timings and the sound palette.
- A **scene library**: each scene type with a keyframe sheet, a one-line "use when", typical duration and build notes.
- **Placement rules**: which script moments get which scene type, measured from the references.

Save these in the project (`style/`). Offer to save the style as its own skill via `propose_skills` so it can be reused.

**Default scene library** (a premium minimal style; replace or extend it with what the references show):

| Scene type | Use when | Build notes |
| --- | --- | --- |
| A-roll + captions | The speaker introduces a new idea; any time the viewer needs the face | Two-font captions (C3) |
| B-roll + text | Describing an action or situation | Paper texture, darkened and slightly blurred edges, caption text describing the scene |
| Painting + text | Philosophical or emotional points | Public-domain artwork, paint and rough-paper texture, text around the subject, slow camera slide-in |
| Line + text | Connecting ideas or a sentence with key words | Paper background, accent-color line draws and is "interrupted" by text; the camera follows the line |
| Line + illustrations | Progression, phases, a timeline | Line with dots marking each stage, zigzag for phases, the camera pans to reveal items |
| Text-centric quote | The thesis or the closing line | Rough paper, large quotation marks, the line written out in the center |
| Center illustration | Naming a concept or a person type | A textured illustration fills the lower half and bleeds into the middle; text around it |
| Side illustration + text | Showing two things at once | Subject on one side, text on the other |
| Object/character callout | A specific person, object or example | One element with text labels and a rough reveal |
| Graph | Numbers, trends, "up and up" | Dark textured background, thin glowing grid, a dot that rides the line with the camera following |

## C2. Prepare the A-roll

- **Transcript**: word-level timestamps (supplied SRT/VTT/JSON, or Whisper if its model is reachable).
- **Silence cuts**: remove silences and filler with ~30 ms of padding; never cut mid-word. Hide jump cuts with alternating punch-ins (1.0 ↔ 1.08 scale) or a scene change.
- Keep the speaker's audio as the master track; everything else is cut to it.

## C3. Captions (two-font emphasis logic)

- One caption group per short phrase (≤ 5 words), timed to the words.
- Pick the 1–2 most important words: big, bold, centered, in either a bold sans or a bold italic serif (the emphasis font). Place the remaining words smaller in the gaps above or below.
- Main font: a clean sans (e.g. Inter or Montserrat). Emphasis font: an italic serif (e.g. Playfair Display Italic).
- Captions sit in the upper-middle safe area (Part D4), never under the platform caption bar.
- Sync check: each word appears within ±2 frames of being spoken.

## C4. The edit plan (human in the loop)

AI planning alone is rarely creative enough, so plan with the user before building:

1. Split the script into beats (one idea, sentence or list item each).
2. For each beat, recommend a scene type from the library (with its keyframe sheet) plus 1–2 alternates and "stay on A-roll".
3. Deliver it as a doc (an editable table: time · script · recommended scene · alternates · notes) so the user can pick and annotate. If the user isn't there, apply the rhythm rules, state the picks and build.

**Rhythm rules:** a new idea is announced → the face (A-roll); it's described → show it (a visual). Numbers → graph. A person or example → callout. A sequence or progression → line. The thesis or final line → quote scene. Never more than ~3 visual scenes in a row without returning to the face. Something changes every 2–4 s.

## C5. Assets

Make an asset list (scene → asset → source → license) before building. Sources, in order: the user's own files; public-domain art (pre-1929 works, museum open-access collections); stock the user supplies or licenses; graphics built in code (lines, graphs, illustrations, textures). Never put downloaded photos of real people into the video: use the user's footage or an illustration. Generate textures in code: grain via SVG feTurbulence, paper fiber overlays, vignettes, rough painted edges, and move them with the camera so they don't look stuck on.

## C6. Build, revise, lock, then sound

1. Build v1 scene by scene from the approved plan and render it. Expect v1 to be 60–70% there.
2. Collect numbered revision notes (text design, rough cuts, texture weight, scene length, missing elements) and apply them with the smallest change each.
3. Ask for picture lock.
4. Only then do the sound pass (Part E): music under the voice, SFX matched to the references.

---

# Part D · Craft rules (both modes)

## D1. Timing

- Anything important (headline, number, key UI state) stays on screen at least ~1.5 s (90 frames at 60 fps).
- Count-ups last about 1 s (60 frames), ease-out, and never jump to the final value in one frame.
- Scene lengths come from the storyboard or the edit plan, and the total matches exactly (30.0 s = 1800 frames by default). Restate the scene list with frame ranges and check the sum.
- Launch mode locks to a beat grid (120 BPM = a beat every 0.5 s = 30 frames): cuts, swaps, taps and reveals land on beats or 8th notes. Style edit mode cuts to the speaker's words.

## D2. Motion

- Nothing moves linearly.
- Entrances: ~0.5 s (30 frames) with a slight overshoot (spring, damping ~14, or cubic-bezier(0.34, 1.56, 0.64, 1)). Exits are faster: ~60% of the entrance, ease-in.
- Every click or tap gets a tiny press: scale 1 → 0.96 → 1 over ~8 frames.
- Cursors and thumbs never move in a straight line: a quadratic-bezier arc (control point offset ~15% of the distance), eased in and out, settling with a tiny overshoot, like a real hand.
- Golden rule: nothing ever fully stops. Holding elements keep a slow drift (scale 1 → 1.02 or ±4 px), and the camera always has a micro-push.
- Work like After Effects: parenting (animate the group, not every piece), offset (each element starts 2–4 frames after the previous one), overlap (start the next move during the last ~20% of the previous one).
- Camera: one camera container per scene. Pans and zooms always ease in-out. A full-width pan takes at least ~0.8 s.
- The transformation moment gets a small camera punch and a brand-color flash.

## D3. Typography and copy

- On 1080 × 1920: secondary text ≥ 36 px, primary 48–72 px, headlines 90–160 px, bold weights. When UI is laid out small and scaled up, check the on-screen size (layout px × scale).
- First-frame text hook for sound-off viewers: 5–8 words, readable at frame 0 (start at ~60% opacity, not 0), on screen 2+ s.
- Fit headlines to the safe width; split or shorten lines that overflow.
- Stacked labels read as grammatical sentences ("REEL 2 · YOUR PEOPLE" + "IS THIS FOR ME?"). Lists use parallel, verb-led phrasing ("Opened your link / Watched … / Asked for updates").
- No orphans: force line breaks (`white-space: pre-line`) so a lone word or "21+." never sits on its own line.

## D4. Layout and vertical 9:16

Build vertical 1080 × 1920 first when the video is for Reels/TikTok/Shorts, then 16:9 and 1:1 as their own layouts (not crops), sharing one config, timing and audio. Position everything from the canvas center.

- Platform UI: keep text and key UI out of the top ~250 px (username, follow), the bottom ~320 px (caption, audio) and the right ~120 px (like/comment/share). Nudge the stage ~20 px left. Then use all the space in between; empty lower thirds read as unfinished.
- If the product lives on a phone, go full-bleed: the viewer's phone is the phone. Lay the product UI over footage at full size. Keep a phone mockup only where a transformation needs it.
- Transformations happen in place. After the 'after' lands, show a compact before/after where the 'after' is clearly bigger and the 'before' lightly shaded, not near-black.
- One focal point at a time, in the upper-middle; the eye never jumps corner to corner. Headline directly above the subject, payoff directly below. Replace content in the same spot rather than adding rows lower down. Put confirmations (toasts, checkout chips) next to the button that was tapped.
- 16:9: titles 5% inside every edge; the key element of every shot inside the center 1080 × 1080 square.
- Mobile needs more pop than desktop: brighter accents, lighter overlays on footage, larger cards.

## D5. Assets and build

- UI is SVG or rebuilt in code, never screenshots, so it stays razor sharp under zoom. Figma frames are usually 1440 px wide: scale each screen by one uniform factor and center it.
- Load fonts before the first frame renders (delayRender until document.fonts.ready). A fallback font is a bug.
- Backgrounds sit behind the UI with a light parallax.
- Re-encode source video with short GOPs (`-g 12`) and no audio before `<OffthreadVideo>` (keep the speaker's audio as its own track in style edits). Cut from real shot boundaries and check every in-point for stray shots.
- When footage is shorter than the scene, slow it down (`playbackRate`) rather than repeat the same shot; never let a clip run past its end.
- Luma-key text lifted off dark artwork to a transparent PNG rather than relying on blend modes.
- Config-first: copy, numbers, colors, timings, clip in-points and scene lengths in config files so revisions are one-line changes. One component per scene (`<Sequence>`); shared Camera, Cursor/Thumb, Counter, captions, Headline, full-bleed UI overlay, Phone, Toast, Card stack, Path/timeline, Split screen, Stamp, Logo reveal, texture layers. Each story angle or edit gets its own config, scenes file and composition.
- If Remotion can't download its browser, pass `--browser-executable` pointing at an installed Chrome Headless Shell. Full renders with video take 10+ minutes per 30 s: run them in the background and poll.
- Render a still of each scene's key frame first (vertical: blocked zones overlaid in red), then the full video. On a fix or revision, change the smallest thing that solves it, keep everything else, re-render.

---

# Part E · Sound (both modes)

- Never ship silent. Prefer a licensed track; otherwise synthesize an original score in code (numpy/scipy → WAV) shaped to the story: intro pad and heartbeat, tension (stamps, risers, a tape-stop) where the story has tension, silence before the turn, the drop on the transformation, an impact on the logo, a soft bed under the CTA.
- Signature move when it fits: start muffled ("outside"), cut to silence, open to full sound plus ambience at the reveal.
- SFX on the action: stamps for objections, whooshes for transitions, ticks/clicks for taps and text pops, a highlighter or rise for graphs, pings for list items, a soft pencil for line draws.
- With speech (style edits): the voice is king. Duck the music 12–18 dB under speech, keep SFX short and below the voice, and do sound only after picture lock.
- You can't listen: check per-second loudness, the drop's jump in dB, true silence where intended, no clipping and no dead air at the end. For loops, the last second's level matches the first.
- Mute source clips' own audio (except the A-roll voice). Add tracks with `<Audio>` at the composition root. Deliver a timed VO script even when captions carry the words.

---

# Part F · Review, QA and deliverables (both modes)

## F1. Review gate: score before you ship

Score the storyboard or edit plan, then the rendered cut, 1–5 on each criterion. Revise anything under 4. Use a fresh-eyes reviewer (a sub-agent if available) so the work isn't grading itself.

| Criterion | 5 looks like |
| --- | --- |
| Hook | Stops the scroll muted in 1.5 s; foreshadows the payoff |
| Character and stakes | The viewer sees themselves and a real problem |
| Causality | Every beat is "but" or "therefore" (style edits: every visual explains what's being said) |
| Payoff | Answers the hook's question and reframes the setup |
| Proof | A real customer, real path or the speaker's own story; nothing invented |
| Clarity | A stranger can say what it's about after one watch |
| Share trigger | A clear reason to send it to a specific person |
| Rewatch | A loop ending or a detail worth a second look |
| Craft | Type, motion, texture, sound and safe areas pass F2 |
| Truth | Every claim traces to the truth table |

## F2. Checks

Pre-render:
- [ ] Canvas locked to the target size; everything positioned from the center.
- [ ] Fonts loaded before frame 0. No Times New Roman anywhere.
- [ ] No overlapping text at any frame (check stills at every scene boundary).
- [ ] Counters animate over ~1 s and never jump in a single frame.
- [ ] Repeated elements (cards, list rows, checkmarks) stagger in and never appear all at once.
- [ ] Every camera move has an easy ease and is slow enough to read.
- [ ] Nothing leaves the canvas unless it is exiting on purpose.
- [ ] Music present, cuts on the beat (or on the words), ending not silent.
- [ ] 9:16: nothing readable in the top 250 px, bottom 320 px or right 120 px; no large empty areas.
- [ ] Style edits: captions in sync (±2 frames), no cut mid-word, the face returns at least every ~3 visual scenes.

Final QA (on the rendered file, not the code):
- [ ] ffprobe: resolution, fps, exact frame count, duration, audio stream present.
- [ ] Contact sheet of one frame per second (per 2 s for 60 s+), blocked zones overlaid: no overlaps at scene boundaries, nothing cut off, no stray shots at cuts. For loops, compare the first and last frames.
- [ ] Zoomed crops of the smallest text: spelling, line breaks, no orphans.
- [ ] Every on-screen claim listed and traced to its source; flagged lines reported to the user.
- [ ] Audio: per-second loudness matches the story (silence, drop, ending bed), voice clear above music, no clipping, no dead air.

## F3. Deliverables

- The master (vertical first for social, plus 16:9 and 1:1 when asked): H.264 mp4, yuv420p, CRF ~16, AAC 320k, 60 fps.
- The score as WAV, a timed VO script (launch mode), a captions file, a suggested cover frame (timestamp).
- Two alternate hooks and a post caption for A/B testing.
- Style edit mode: the edit plan doc and, after a style is learned, the style sheet and scene library (offered as their own skill).
- The project zip, plus a short list of decisions the user still owns (permissions, claims to confirm, assets to swap in).

## References

- `references/brief-template.md`: the client brief format.
- `references/storyboard-template.md`: the scene-by-scene storyboard format, with a filled example.
- `references/pitch-message.md`: the proposal template for landing launch-video clients.