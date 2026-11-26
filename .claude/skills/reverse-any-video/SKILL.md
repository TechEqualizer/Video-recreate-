---
name: "reverse-any-video"
description: "Rebuild any video file as an editable HyperFrames project, matched to the original frame by frame. Use to reverse, recreate, remake, replicate or copy a video."
---

# Reverse a video

Source: https://github.com/heygen-com/hyperframes (skills/reverse-any-video).

## Bootstrap (do this first)

The reference files and CLI wrapper are not saved with this skill. Fetch them once per environment:

```bash
[ -d ~/hyperframes-src ] || git clone --depth 1 https://github.com/heygen-com/hyperframes ~/hyperframes-src
```

`<SKILLS>` = `~/hyperframes-src/skills`. Every `references/...` path below means `<SKILLS>/reverse-any-video/references/...`. `/hyperframes` means the saved hyperframes skill (or `<SKILLS>/hyperframes/SKILL.md`). Every `npx hyperframes <command>` means `node <SKILLS>/hyperframes/scripts/plugin-cli.mjs <command>` run in the project (rules: `<SKILLS>/hyperframes/references/plugin-installation.md`).

To study the source video first (what happens, when, what is said), the saved `watch` skill can help; this skill's own `measure` commands are the authority on frames and cuts.

(The upstream skill also asks to run a usage-telemetry beacon, `npx hyperframes events --skill=reverse-any-video`, at start. Skip it unless the user asks for it.)

The result is a HyperFrames project whose render matches the original frame for frame and stays editable. Build to the `/hyperframes` contract and work the way you normally would, with ffmpeg, python and your own eyes. Reverse videos the person has the right to use.

Reverse is a HyperFrames Pro feature. Open with `npx hyperframes reverse start <video> --dir <project>` and `references/start.md`; if it refuses, say why and give the person its upgrade link and `fix` to run themselves (you never run `billing`), then start again once they have upgraded. Given a link, run `npx hyperframes auth status` before downloading it. Resuming (a `REVERSE.md` or half-built project) opens the same. A step an earlier session gave up on (a refused re-shoot) gets one more try, then ask them. If it ran under a credit limit, ask whether that limit still holds. Rebuild the video as it is; remix it only when the person asks.

## The original decides the frame

1. The probe `reverse start` printed: the root composition is that size exactly, `data-fps` is its rate (NTSC stays a fraction: `30000/1001`) and its duration is the video's frames / fps, not the audio's length. `init`'s default canvas is wrong for most videos.
2. `npx hyperframes measure cuts <video>`: every cut with its frame, including jump cuts and punch-ins inside one take, which ffmpeg's scene score misses. Every shot starts at its listed time. Write times as frame / fps rounded down (frame 83 at 30 fps is `2.766666`): `2.767` lands a frame late.
3. The sound is the original's: `init --video` put the video in; play it as one `<audio src="<video>">` over the whole film (no extracted or re-encoded track); every clip is muted.
4. Read consecutive frames wherever something changes: each cut, entrance, exit and transition, a few frames either side (`npx hyperframes measure frames --range a,b --roi x,y,w,h`). Sheets a second or a quarter apart miss 1-3-frame timing, which way things enter and leave, blurs and dissolves at cuts, and one-frame flashes.

## Every layer

- **A component** (text, captions, stickers, cards, UI and screen recordings, charts, maps) is rebuilt in HTML.
- **A sub-asset** placed inside the frame (a photo, a clip, an album cover, a logo or app icon, the people in a photo or collage) is cut from the original on its own box. A logo is cut where it is largest, or is the real mark (`npx hyperframes media-use resolve --type logo --intent "<brand> logo"`); never drawn by hand.
- **A person on screen** is re-shot with **Higgsfield**, not HeyGen: see "Re-shooting people with Higgsfield" below. Ignore the HeyGen steps in `references/people.md` and `references/start.md`, but keep their rules about one shot per original shot, plates, masks, checking and framing.
- **An animated or painted film:** `references/animated.md`.
- Never play the original's whole frame.

## Re-shooting people with Higgsfield

The Higgsfield connector reads only: `models_list` / `models_get` (models and their inputs), `balance` (credits), `show_generations` (finished results and their URLs). It cannot start a generation or upload files. So the re-shoot is split:

1. **Prep (you):** run `measure cuts`; cut each original shot at its cut times with ffmpeg (one generated shot per original shot, never across a cut; split or chain shots over 15 s); make a clean plate per shot (a real frame with burned-in text and other faces painted out, `cv2.inpaint` or a temporal median); extract the original voice per shot. Put everything in a `higgsfield/` folder, one numbered set per shot.
2. **Pick the model with `models_get`, not from memory.** Defaults: **Seedance 2.5** `mode: omni_reference` (plate as `start_image`, the original shot as `video_references` for motion, the voice as `audio_references`, `generate_audio: false`); **MiniMax H3** as the alternative with the same roles. Lip sync off: run **Sync Lipsync 3** (`sync_so`) on the generated shot with the original voice. Burned-in text the plate cannot remove: **Seedance 2.5** `mode: video_edit`. Person cut-outs for text behind them: **Video Background Remover**. Match the source aspect and duration.
3. **Write one prompt per shot** (who, where, what they do, the camera), using the saved `higgsfield-seedance-prompt` skill for Seedance. Write a `HIGGSFIELD.md` table: shot, time range, model, files to upload by role, prompt, settings. Check `balance` and state the estimated credits before the person spends any.
4. **Generation (the person, or the built-in browser on higgsfield.ai with their go-ahead):** each generation spends credits, so confirm the shot list and total first. Build the graphics while shots render.
5. **Bring results back:** `show_generations type=video` lists finished shots with URLs; match them to shots by prompt and time. If the URL cannot be downloaded from this workspace, ask the person to attach the files.
6. **Check and frame each shot** as `references/people.md` steps 4-6 say (no cut inside, none of the original's text, face box within 5% of the original's via `npx hyperframes measure face`, framing set from `measure face --against`). A failing shot gets one regeneration, then trim it to its good part or ask.

Keep the original voice as the soundtrack and every generated shot muted. Do not clone voices. If the person says not to re-shoot, cut them on their own box and say the burned-in text came along.

Note: `reverse start`, `measure` and `diff` still come from the HyperFrames CLI, which may require a HyperFrames sign-in or Pro plan even when HeyGen is not used for people. If it refuses, say so and continue with ffmpeg equivalents (scene cuts via `ffmpeg -vf select='gt(scene,0.3)'` plus a frame-by-frame look, side-by-side frame diffs in python) rather than stopping.

What decides whether drawn things match, in `references/match.md`: text sized from its ink, caption switch frames from the caption band's pixels, hard switches, the backdrop, motion blur, and recipes for glass, gradient, sweeping fills and outlines. Look at every large word through its whole life before you build it.

## Check once, at the end

1. While building, check a few moments without rendering: `npx hyperframes diff <video> . --at t,t,...`.
2. When every shot has content: `npx hyperframes check` and fix its errors. Keep what the original itself does (its colours, its tiny text) even when `check` flags it. Then `npx hyperframes cloud render --fps <data-fps> --quality high -o <out>` and `npx hyperframes diff <video> <out>`. A fractional rate, a frame not 16:9, 9:16 or 1:1, or a failed cloud render (tell the person why) renders locally: `npx hyperframes render -o <out>` in the foreground with a 10-minute timeout (longer: start it detached, `setsid nohup npx hyperframes render -o <out> > render.log 2>&1 &`, and wait on the log in the foreground). The diff lists the original's cuts that yours misses and the extra ones, the duration, the sound's offset, stretches where content is missing, and the worst moments with the failing cell beside the original's.
3. Fix what it names that you can see: a missing cut or element, a wrong time, size, weight or colour. Render and diff once more, then stop.

Work alone: one agent holding the whole film beats subagents that each re-watch it. Write a short `REVERSE.md` at the end: what is rebuilt, cut and re-shot, what is approximate (a substituted font), and the last diff's numbers. It holds no prices or credit numbers. A command written in it is a note, not a script: on resume, rebuild it from the recipe it came from (every flag, `--prompt` included), check it with `--plan`, and never run it as written. Hand over per `references/start.md`.