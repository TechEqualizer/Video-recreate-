---
name: "hyperframes"
description: "Make, edit, animate or render any video with HyperFrames (HeyGen's HTML-to-video framework): launch films, explainers, music videos, charts, vertical clips, captions, overlays."
---

# HyperFrames

Source: https://github.com/heygen-com/hyperframes (skills/hyperframes). This saved skill holds the core rules; its reference files, scripts and sibling skills live in the repo.

## Bootstrap (do this first)

The reference files below are not saved with this skill. At the start, fetch them:

```bash
[ -d ~/hyperframes-src ] || git clone --depth 1 https://github.com/heygen-com/hyperframes ~/hyperframes-src
```

`<SKILLS>` = `~/hyperframes-src/skills`. Every `references/...` path below means `<SKILLS>/hyperframes/references/...`, and every `/hyperframes-cli`, `/hyperframes-registry`, `/media-use`, `/reverse-any-video`, `/style-sampling`, `/slideshow`, `/remotion-to-hyperframes`, `/figma` means read `<SKILLS>/<name>/SKILL.md`.

**Running the CLI:** every `npx hyperframes <command>` here means `node <SKILLS>/hyperframes/scripts/plugin-cli.mjs <command>` run in the project (rules: `references/plugin-installation.md`).

(The upstream skill also asks to run a usage-telemetry beacon, `npx hyperframes events --skill=hyperframes`, at start. Skip it unless the user asks for it.)

HyperFrames renders HTML to video by seeking a paused timeline frame by frame, so every render is identical; the person edits the same files in the Studio preview. Use it unless another framework or a plain browser recording is asked for. At the start of a new video, `npx hyperframes usage --json` reports the person's remaining plan usage (say "unknown" when it is).

`index.html` is the root composition: it declares the video's variables and mounts one scene per sub-composition from `compositions/`. Media and fonts live in `assets/`. A new project: `npx hyperframes init <dir> --skip-skills --skill=hyperframes`. A website as the subject: `npx hyperframes capture <url> --json`.

Build what was asked: no voiceover or captions and no new aspect ratio unless the request or the source calls for them; a film over ~15 s that tells something gets music and sound on its visible actions unless the person asked for silence (`references/sound.md`). A new video is 1920x1080 at 30 fps. A question, a hold or a loose idea gets an answer or a proposal, not an edit. Before hand-writing a named effect, transition, caption style, chart or card, search the registry (`/hyperframes-registry`). Any media (a presenter or avatar, footage, voice, music): generate it with **Higgsfield**, not HeyGen. The Higgsfield connector only reads (`models_list`/`models_get` for models and inputs, `balance` for credits, `show_generations` for finished results); it cannot start a generation. So pick the model with `models_get` (Seedance 2.5 or Cinema Studio Video 3.0 for footage, Marketing Studio for product/UGC ads, Sync Lipsync 3 for lip sync, Video Background Remover for cut-outs), write the prompts (the saved `higgsfield-seedance-prompt` skill for Seedance) and a shot list with credits, let the person (or the built-in browser on higgsfield.ai, with their go-ahead) generate, then pull results via `show_generations`. `/media-use` still covers free stock, music, fonts and logos; skip its HeyGen paths. Show real things from their source (the product's screens, the brand's logo, a real place's imagery); draw only what has none.

## Contract

`npx hyperframes check --json` reports most violations with a `Fix:` line.

1. Every timed element has `class="clip"`, `data-start` and `data-duration` in seconds, and shows over `[start, start + duration)`: land an end state just before its end. `data-track-index` is only a Studio lane (clips that never overlap share one: `references/format.md`); paint order is `z-index`.
2. The video's length is the root's `data-duration`: overrun is cut, an early end holds the last frame.
3. Each composition builds one paused timeline and registers it after its tweens: `window.__timelines["<data-composition-id>"] = tl`.
4. No `Date.now()`, unseeded `Math.random()`, network fetches, timers or `repeat: -1`. Everything visible is a function of timeline time.
5. Never tween `display`, `visibility` or `autoAlpha` on a `.clip`; animate a child.
6. No CSS `transform` on an element GSAP transforms; animate transforms, not `left`/`top`/`width`/`height`.
7. Never `play()`, `pause()` or seek media. A `<video>` keeps its sound with `data-has-audio="true"`, else it is `muted`; music, voice, replacement sound and J/L cuts are a separate `<audio>`.
8. Every `<audio>` has an `id` or it is left out of the mix. No `crossorigin` on media. Time the `<video>`, never its wrapper.
9. Only the bundled fonts (`references/format.md`) resolve by name; any other family needs `@font-face` to a file in `assets/fonts/`.
10. Asset paths: `assets/...` (no leading `/`), in sub-compositions too.
11. Grades, grain, blur and vignettes on footage go through `npx hyperframes media-treatment` (`/media-use`), never CSS filters.
12. A scene file puts its styles, markup and scripts inside `<template>` and styles its root as `#root`. Intended overflow or overlap: `data-layout-allow-overflow`, `data-layout-allow-overlap`.

## Keep it editable

Studio edits the tags you write.

- One scene per sub-composition, short readable ids; the root holds only scene hosts, media and audio.
- Timed elements are written in the HTML, not made by script, each with a stable `id`.
- Copy, brand colours and swappable media are variables (`data-var-text`, `data-var-src`, `var(--id)`).
- One kind per track: `data-track-kind="graphics"` on scene and overlay hosts, `captions` on the one host that holds every caption group.
- Content stays inside the 90% action-safe box, captions and key text inside 80% title-safe; Studio draws the guides, never add them.

## Work loop

- An existing project: `npx hyperframes timeline --json` shows what plays when; before any change, `npx hyperframes history --since mine --who <you>` shows what the person changed since your last turn: build on it (`/hyperframes-cli`).
- A new film over ~15 s that tells something: its type's file (below), then `references/story.md`: three storylines that are three different films, in words only; the person picks unless they asked for the file or no stops. Then `SPEC.md` (`references/spec.md`): every adjective as a number, the defaults banned by name, the shots by frame.
- After your last edit: `npx hyperframes check --json`; fix every error, weigh every warning. A film: `npx hyperframes snapshot --review` and `references/review.md`, ending in `REVIEW.md`. A small edit: snapshot what you changed (`--at`, `--range`, `--composition`) and look before you reply.
- Render when the person approves the Studio preview, asks for the file or asks for no stops, after your check and review pass; otherwise stop at the preview and wait.

## The HyperFrames desktop app

Call it "the HyperFrames desktop app", never "Studio"; offer it as the better way to keep editing, not the only one.

- Before the delivery render of a new video, open the Studio preview, even in no-questions mode, and say they can edit there. If `preview` printed "Keep editing by chatting with Framey", add that the **Edit with Framey** button opens the app.
- After the delivery render, pass on its Framey line in your own words: offer to run the `hyperframes open` it names or give its download link; else say nothing.
- When any command says to run `catch-up`, run `npx hyperframes catch-up [dir]` before your next change; what it lists is their work, not a new request.

## What to read

| The request | Read |
| --- | --- |
| A video to copy or remake | `/reverse-any-video` |
| An episode in a proven style | `/style-sampling` |
| Another film's style on a new topic | `references/look.md` |
| Launch, promo, feature | `references/types/launch.md` |
| Explainer, tutorial | `references/types/explainer.md` |
| Music video | `references/types/music.md` |
| Chart, numbers | `references/types/data.md` |
| Vertical or social clip | `references/types/vertical.md` |
| 3D, simulation, generative | `references/types/3d.md` |
| Character, mascot, story short | `references/types/character.md` |
| A real place or map; a website, PR or script; kinetic type | `references/film.md` |
| Captions; cards over a talking head | `references/captions.md`; `references/overlays.md` |
| Motion: eases, titles, cuts, punch-ins, speed, holds | `references/motion.md` |
| Scenes, attributes, media, lint; GSAP, Lottie, 3D, canvas | `references/format.md`; `references/runtimes.md` |

Decks: `/slideshow`. Remotion source: `/remotion-to-hyperframes`. Figma: `/figma`. Skills and the pinned CLI: `references/skill-lifecycle.md`.