---
name: "premium-motion"
description: "Premium software/product ad style: real 3D devices and glass UI rendered in code, spring physics, simulated touches, live UI and designed match-cut transitions. Use when the product or UI is the hero."
---

# Premium Motion (the "$1M launch film" style)

A production module for the **Premium 3D UI** style in `style-director`. Use it for software, apps and platforms (FLMLNK dashboards, Showlnk, SportLnk, ChairLnk) when the product itself should look expensive. It can also supply scenes inside a longer film (for example the product section of an investor film). Higgsfield footage handles people and places; this module handles devices, glass and UI.

Adapted from a production brief by Zane Hoyer ("Premium Animations").

## Phase 1: Analyze (no code yet)

From the references, write `style/bible.md`:
- palettes in hex; lighting (soft studio light, softbox highlights, rim light)
- materials (matte titanium, frosted glass, glossy ceramic, iridescent pearl, liquid chrome)
- camera language (tilted 3/4 angles, floating objects, soft contact shadows)
- typography (one grotesk family, tight tracking at display sizes)
- composition patterns (floating devices, glass chips and pills, cards fanned in depth, huge background type, marquee words)
- what specifically makes each reference feel expensive
Plan a 6-scene story that uses the strongest idea from each reference, with one recurring logo mark (a simple geometric 3D form). For Dw's own brands use the real brand; for a demo with no brand, invent an original one. Never copy names, text, logos or characters from references.

## Phase 2: Storyboard (stop for approval)

Render six key frames at full resolution, one per scene, at the moment with the most on screen. Inspect each at full size plus detail crops: clipping, blown highlights, washed-out colour, overlapping text, scale problems, stray template text. Send the six frames and a labelled contact sheet (one line per scene) and wait for Dw's approval. If the quality bar cannot be met, say which external assets would help.

## Phase 3: Animate (only after approval)

Write a beat sheet with timings for every scene first. Nothing may simply slide in.

**Springs, not tweens.** Closed-form damped spring:
`x(t) = 1 - e^(-z*w*t) * (cos(wd*t) + (z*w/wd) * sin(wd*t))`, with `w = 2*pi*f` and `wd = w*sqrt(1 - z^2)`.
- Heavy objects: f 0.9 to 1.2 Hz, damping z 0.55 to 0.8
- UI pops: f 2.0 to 2.6 Hz, damping z 0.38 to 0.5 (visible overshoot)

**Pop-in:** scale from 0.3 to 0.6 with spring overshoot, opacity in over 0.2 s, blur 10 px to 0, plus a small settling rotation or offset.

**Text:** split into words or characters; each rises 0.4 to 0.6 em, fades in and un-blurs from 8 to 22 px, ease-out-expo about 0.9 s, stagger 30 to 90 ms. Exits reverse with blur.

**Notifications:** drop in on a bouncy spring, the icon pops a beat later, lines cascade in, the device gives a tiny haptic wiggle.

**At least one simulated touch per scene:** a translucent touch circle appears, presses (squish), emits a ripple ring, and the UI visibly responds (button squish and state morph, toggle flip, swatch recolours the product, heart fills with a particle burst, card swipes away, widget opens like an app).

**Live UI:** counters count up, progress bars fill with a moving shine, EQ bars and waveforms move, timers tick.

**Nothing is ever dead:** idle drift on every object (sum of slow sines), a slow camera push or orbit, marquee background type, breathing glows, animated grain (offset the grain texture every frame).

**Motion blur on 3D:** average several shutter samples per frame (180-degree shutter); 1 sample when slow, up to 6 or 7 when fast.

**Scenes run 5 to 6.5 s. Transitions are designed match cuts, never crossfades between unrelated shots:** iris reveal through a ring flying through camera (alpha cut-out composite); push into a phone screen whose app-opening panel matches the next scene's background; whip pan with horizontal directional blur peaking at the cut; a tap ripple that floods to black into a dark scene; bloom to white into a bright finale.

## Technical approach (proven)

- Each scene is an HTML page: HTML/CSS for UI, text and glass; a WebGL2 canvas for 3D. Render in headless Chromium via Playwright at 1920x1080 CSS with deviceScaleFactor 2 (4K). Expose `window.SCENE.frame(t)` that sets every style and transform purely from `t`. Serve over a local HTTP server (file:// breaks WebGL textures).
- For animation use a small WebGL2 triangle rasterizer, not a raymarcher (raymarching is fine for stills only). Mesh generators: rounded slab (phones, glass tiles, cards), torus and torus arc, sphere, lathe (cylinders, lenses, capsules).
- Shading: analytic studio environment (sky/ground gradient plus 2 or 3 rectangular softboxes for key, strip fill and rim) driving diffuse and Fresnel reflections; roughness widens softbox edges; clear-coat layer; iridescence as a view-angle cosine palette; glass as refraction into an analytic background plus bright edges; 4x MSAA.
- Phone screens and widget faces: each screen is its own HTML page with `setT(t)`, screenshotted every frame and uploaded as an emissive texture under a glass reflection layer. Phone model: titanium frame, curved black glass edge, bezel, dynamic island drawn in the UI, camera plateau with lenses, logo on frosted back glass.
- Contact shadows: blurred radial-gradient divs under objects, scaled and faded with height.
- Pitfalls: software GL runs every branch of an uber-shader, so compile one program per material; triangle fans are slow, so triangulate faces as grids; never build 3D objects from stacked CSS 3D layers (they tear and z-fight); when a canvas changes size, convert focal length relative to image height; text-splitting helpers must not destroy child elements still referenced.
- Art inside screens (wallpapers, covers) can be raymarched once per page load, or generated with `gpt_image_2_6`.

## Where it runs

The Higgsfield sandbox has Playwright with headless Chromium: build there, render with `size: xl`, keep each call under 60 s and poll background jobs. Expect 30 to 60 minutes of render time for 30 s at 4K; render a 1080p preview first. Tell Dw the estimate up front.

## Quality control

- Before any full render, render every scene at quarter resolution, sampling every 0.4 s, build contact sheets and review timing, framing and transitions. Fix and re-check.
- Spot-check full-resolution crops for edges, text crispness and materials.
- Render scenes to JPEG frames (PNG with alpha only where a transition needs it). Assemble in one pass: composite transitions in numpy and pipe raw frames to ffmpeg (libx264, -preset medium, -crf 15, yuv420p, +faststart, 30 fps). Write to a temp name and rename on success.
- Verify with ffprobe and sample frames around every transition.

## Deliverables

1. Phase 2: six storyboard frames plus a labelled contact sheet, then wait for approval.
2. Phase 3: the 3840x2160 30 fps master, a 1080p preview, and a short beat-by-beat summary of the motion and transitions.
Keep messages short: show results, not process.