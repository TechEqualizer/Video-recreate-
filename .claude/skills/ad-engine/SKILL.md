---
name: "ad-engine"
description: "Turn a short brief (product, audience, offer) into a finished, photoreal video ad matched to a reference ad's look: concept, Higgsfield footage, coded type and sound, QA, and A/B variants. Use for any ad, commercial, promo or UGC ad request."
---

# Ad Engine

One system that runs Dw's video skills in the right order so a short brief becomes a finished, realistic ad. This skill is the director; the other skills are the departments. Load each one only at the step that needs it:

| Department | Skill | Used for |
| --- | --- | --- |
| Story, truth, craft, sound, QA | `launch-motion` | Truth table, angles, storyboard, motion and type rules, score, review gate |
| Shot prompts | `higgsfield-seedance-prompt` | Every Seedance prompt, no exceptions |
| Footage, stills, voice, music | Higgsfield connector (`mcp__Higgsfield__*`) | All generated media. Never HeyGen |
| Edit and finish in code | `launch-motion` (Remotion, default) or `hyperframes` (when Dw wants to keep editing in the HyperFrames app) | Type, captions, UI, logo, CTA, assembly |
| Rendering | `video-making` | Per-scene files, concat, one full render |
| Learning from a reference ad | `watch`, `reverse-any-video` | Study or rebuild an ad Dw points to |

## 1. Intake: five lines, asked once

Read memory and any attached files first; ask only for what is missing, in one message, with the default stated.

1. **Product** (link, photos or screen recordings) and which brand it belongs to
2. **Audience** and where they will see it (default: Reels/TikTok, 9:16, sound-off first)
3. **Offer and CTA** (what is true: price, deadline, guarantee)
4. **Length** (default 15 s; 30 s when the story needs a proof beat)
5. **Reference** (1 to 3 ads whose look this one must match; default bar is Higgsfield's own YouTube ads)

Then build the four tables from `launch-motion` Part A (truth table, audience sheet, brand tokens, asset inventory). Nothing outside the truth table reaches the screen.

## 2. Pick the route

| Route | When | Engine |
| --- | --- | --- |
| **Cinematic product film** (default for physical products) | Product is the hero: apparel, objects, food, places | Keyframe stills, then Seedance 2.5 or Kling 4.0; finished in code |
| **Creator / UGC** | Trust and demonstration sell it | Load Higgsfield workflow `ugc-video` |
| **Product-in-motion (software)** | SaaS, apps, platforms like FLMLNK or Showlnk | `launch-motion` launch mode; real UI rebuilt in code, with 1 to 3 generated live-action shots for the human pain and payoff |
| **Story ad** | A character with a problem, 30 to 60 s | Higgsfield workflow `drama-ads` (only when Dw picks it), or multi-shot Seedance |
| **Remix a working ad** | Dw has an ad that performs and wants versions | Higgsfield workflow `ad-multiplier` |
| **Static ads** | Meta feed images | Higgsfield workflow `ads-studio` |

Before the first call of any Higgsfield workflow, load it with `get_workflow_instructions`.

## 3. Match a reference (the quality bar)

"Stunning" is measured against a named reference, never judged in the abstract. Every ad starts from 1 to 3 reference ads Dw links or uploads.

1. **Get the reference in.** Try `watch` first. If the workspace cannot reach the site (YouTube is often blocked), import the link into Higgsfield with `media_import_url` and analyze it there (`video_analysis_create`), or ask Dw to attach the file. If none of these work, say so and ask. Never describe a reference that was not actually watched.
2. **Break it down shot by shot** into `style/reference.md`: shot count and average shot length, cut rhythm against the music, each shot's size, FOV, camera move and speed, lighting setup and Kelvin, grade, texture and grain, transitions, type treatment and placement, sound design per cut, and the 2 or 3 signature moves that make it feel expensive (for example speed ramps, whip transitions, macro product inserts, orbit moves, match cuts).
3. **Turn that into numbers the build must hit:** cuts per 10 s, longest hold, share of shots with camera motion, number of macro inserts, number of signature moves, loudness shape.
4. **Borrow the craft, not the content.** Structure, pacing, camera language and finish are fair to learn from. The reference's footage, people, logo, music, characters and exact shots are never copied.
5. **Use Higgsfield's own machinery when the route allows:** Marketing Studio templates and an `ad_reference_id` for product ads, the `katana` workflow for a remix in a reference's visual language (only when Dw selects it), camera and motion presets from `get_presets`. These are the tools their own ads show off.
6. **Finish like a post house.** Reference-grade ads are not raw generations. After picture lock: one consistent grade across every shot, upscaled finals, speed ramps and transitions built in the edit, and sound designed on every cut.

Once a reference style is learned, offer to save it as its own skill so later ads skip this step.

## 4. Concept before shots

Follow `launch-motion` B1 to B3: three loglines from different angles, scored on the rubric, one picked, a storyboard with frame ranges. Use these ad skeletons, adjusted to the reference's cut rhythm:

**15 s (450 frames at 30 fps)**
- 0.0 to 1.5 s: hook. The result or the pain, in motion, plus a 5 to 8 word text hook readable at frame 0
- 1.5 to 5 s: the problem, with real stakes, in the audience's words
- 5 to 11 s: the product fixes it, in one continuous move. The hero shot lives here
- 11 to 13 s: one proof beat from the truth table
- 13 to 15 s: logo, offer, CTA. Last frame matches the first for a loop

**30 s**: same spine, each beat doubled, plus a second hook at ~8 s and a share-trigger line before the CTA.

**YouTube pre-roll**: 16:9, the first 5 s must work before the skip button, and the brand appears inside those 5 s.

Show Dw the three loglines and the storyboard as one short message. If he is away, pick the top score, say which, and continue up to the first spend gate.

## 5. The realism system

This is what separates a real-looking ad from an AI-looking one. Apply all of it.

1. **Keyframe first.** Never go straight from text to video for a hero shot. Generate the first frame as a still (`gpt_image_2_6` for general photoreal, `marketing_studio_image` for product), get it right, then animate it as `start_image`. Fixing a still costs a fraction of fixing a video.
2. **The real product is always a reference.** Upload the actual product photos or the print file (`media_upload`, PUT, `media_confirm`) and pass them as references in every shot the product appears in. State logos, print text and colors in words too. Reject any take where the product drifted.
3. **Light like a set, not like a render.** One motivated key source with a direction, a Kelvin value, and visible falloff. Camera on the shadow side. Add haze or practical lights in the background for depth.
4. **Write imperfection in.** Pore-level skin, flyaway hair, fabric creases, fingerprints on glass, dust in the light, slight handheld breathing (1 to 2 cm), natural motion blur, fine grain. Clean and symmetrical reads as fake.
5. **Physics you can see.** Weight, inertia, contact shadows, cloth that lags the body, liquid that settles. Give speeds in km/h.
6. **Short shots.** 2 to 4 s on screen each, cut from 5 s generations. Keep the best second and a half. Long takes are where faces and hands drift.
7. **One action per shot.** One subject move plus one camera move. Complex choreography goes across cuts, not inside one generation.
8. **Motivated camera on every shot.** Push, orbit, crane, tracking or macro slide, with a stated speed. A locked-off frame is a deliberate choice, used once.
9. **Hands and faces.** Keep hands doing one simple thing, or out of frame. Faces at MCU or wider unless the shot is an identity-locked close-up at 18 degrees FOV.
10. **No generated text, ever.** Headlines, prices, captions, UI, logos and the CTA are built in code over the footage, so they are sharp and correct. Product print text is the only exception, and it comes from the reference.
11. **One look across the ad.** Same white balance, grade, lens character and grain in every prompt's LIGHTING, COLOR GRADE and STYLE blocks. Reuse the same character and location references in every shot.
12. **People.** Cast AI-generated adults or Dw's own footage with permission. Never a real person's likeness, never a photo pulled from the web. Default casting for Dw's apparel stores follows his `printful-tee-mockups` skill.
13. **Draft, then finalize.** Seedance 2.5 `draft: true` (480p) for every shot first. Finalize only the picks at 1080p with `draft_job_id` and `bitrate_mode: high`.

## 6. Production pipeline

Keep a task list. Stop at each gate.

1. **Shot list.** One row per shot: beat, duration, shot size and FOV, what is in frame, model, references, and its credit cost from `get_cost: true`. Check `balance`.
2. **GATE 1, spend approval.** Show the shot list with the total credits for stills, drafts, finals and upscales. Generate nothing until Dw approves that exact total. If the plan grows, ask again.
3. **Keyframes.** `generate_image_batch` for independent shots; `count` 2 to 4 for variants of one shot. Look at every still at full size. Regenerate failures before any video.
4. **GATE 2, keyframe approval.** Show the stills in story order next to frames from the reference. This is the cheapest place to change direction.
5. **Prompts.** Load `higgsfield-seedance-prompt` and write one sealed prompt per shot. Each generation has no memory, so every prompt carries its own references and locks.
6. **Drafts.** `generate_video_batch`, then `jobs_wait` in groups of 12 or fewer, then one `show_generation_by_ids`. On a transport timeout, do not resubmit until the original outcome is known.
7. **Select and finalize.** Pull the drafts down, extract frame sheets, judge each on product fidelity, hands, faces, physics and continuity. Finalize the picks. Re-prompt a failed shot at most twice, changing one thing each time; on a third failure, simplify the shot.
8. **Upscale and grade.** `upscale_video` on the finals (Topaz 2160p for a 16:9 YouTube master; 1080p is enough for vertical social). Then one grade across all shots so they read as one shoot.
9. **Edit in code.** Build per `launch-motion` Part D: config-first, one component per scene, footage re-encoded with short GOPs, type and safe areas per D3 and D4, cuts on the beat grid, speed ramps and transitions from the reference sheet, a slow push on every shot so nothing fully stops.
10. **Sound.** After picture lock, per `launch-motion` Part E. Music from `generate_audio` (`suno_music`) or a score synthesized in code; voice with `seed_audio`; SFX with `mirelo_text_to_audio` on every cut and visible action. Generated clip audio is muted unless it is the point of the shot. Never ship silent.
11. **Render.** Per `video-making`: stills of the busiest frames first, one encoded file per scene, concat with `-c copy`, one full render.
12. **Review gate.** Score on the `launch-motion` F1 rubric with a fresh-eyes reviewer; fix anything under 4. Add **Realism**: no drifted product, no warped hands or faces, no garbled text, no flicker at cuts. Then run F2 final QA on the rendered file.
13. **Parity check.** Put contact sheets of the reference and the cut side by side, one frame per second, and compare against the numbers in `style/reference.md`. The reviewer names every place the cut looks cheaper than the reference (flat light, soft detail, static camera, slow cut rhythm, thin sound). Fix those, or tell Dw plainly which gaps remain and what closing them would cost. Never call the cut equal to the reference unless this check passed.
14. **Optional.** `virality_predictor` on the final cut when Dw wants a hook and retention read. Treat it as one opinion, not a forecast.

## 7. Model picks

The catalog changes. Confirm with `models_explore` (action `get`) before the first generation of a project.

| Need | Model | Notes |
| --- | --- | --- |
| Hero and general footage | `seedance_2_5`, mode `omni_reference` | 4 to 30 s, start and end frames, up to 30 image refs, draft mode |
| Keyframe-to-keyframe moves, 1080p multi-shot | `kling4_0` | Ordered keyframes, 3 to 30 s |
| One-click product or UGC ad | `marketing_studio_video` | 12 to 15 s; pass `aspect_ratio` explicitly |
| Versions of an existing ad | `ad_multiplier_v2` via the `ad-multiplier` workflow | Source must be 4 to 30 s |
| Swap a product or garment into a clip | `hf_mult_replace_object` | One source video plus reference images |
| Stills | `gpt_image_2_6`; `marketing_studio_image` for product | |
| Voice, music, SFX | `seed_audio`, `suno_music`, `mirelo_text_to_audio` | |

Use one Higgsfield project folder per ad and pass its `folder_id` on every generation.

## 8. Deliverables

- Master: 9:16 at 1080 x 1920 for social, or 16:9 at 1920 x 1080 / 4K for YouTube. H.264, yuv420p, AAC. Other ratios as their own layouts when asked, not crops
- Three hook variants: same body, different first 1.5 s (new text hook, and a new opening shot when credits allow)
- Captions file, cover frame timestamp, post caption, timed VO script
- The project folder, the reference style sheet, the shot list with what each shot cost, and the list of decisions Dw still owns (claims to confirm, permissions, assets to swap)

## 9. Honesty rules (not optional)

- Every claim traces to the truth table. No invented results, prices, discounts, deadlines, stock levels or guarantees
- An AI-generated creator can present, demonstrate or act a POV scenario. They never say or imply they are a real customer, and no review, testimonial, rating or before/after result is invented
- The product on screen looks like the product that ships. No generated features, colors or fits it does not have
- No real person's face or voice without their permission. No other brand's logo, footage, music or characters
- Flag anything a platform would require labeling as AI-generated, and leave that choice to Dw

## 10. Running unattended

If Dw is not there to answer: take the most reasonable reading, do everything free (tables, loglines, storyboard, reference breakdown, prompts, shot list, cost quote), and stop at GATE 1 with the total. Never spend credits without his yes to the exact number.