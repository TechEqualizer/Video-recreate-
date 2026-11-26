---
name: "style-director"
description: "Pick the right creative style for any video (ad, investor film, explainer, promo) before production: analyse the brief, score a style library, test two directions cheaply, then hand off to ad-engine."
---

# Style Director

The generation models cannot be retrained. Intelligence lives here: in what the system decides before anything is generated. This skill runs **before** `ad-engine`, `launch-motion` or `hyperframes`. Its output is a locked Style Spec that every later step must obey. Never fall back to a house look (dark background, red accent, line art) unless the scoring picks it.

## 1. Read the brief like a creative director

Fill this sheet from the brief, Dw's memory files and any attachments. Ask only for what is missing, in one message.

| Field | Question |
| --- | --- |
| Audience | Who watches, what do they already believe, what do they doubt? |
| Single job | The one thing they must feel or do after watching |
| Channel and context | Feed (sound off, 3 s to hook), email link (sound on, seated), live pitch, website |
| Length | Seconds, and whether a shorter cut is also needed |
| Story shape | Analogy, problem-solution, founder story, demo, data reveal, manifesto |
| Proof type | Numbers, product UI, people, before/after, logos, none yet |
| Emotional arc | Start feeling, turn, end feeling |
| Assets on hand | Footage, screens, photos, logo, founder on camera |
| Constraints | Budget in credits, deadline, claims that need care |

## 2. The style library

Each style is a complete system. Score every style 0 to 5 against the sheet, show the top three with one-line reasons, and recommend two.

| Style | Looks like | Best when | Voice | Music | Pace |
| --- | --- | --- | --- | --- | --- |
| **Documentary prestige** | Photoreal footage 70%+, slow pushes, lower-third type, natural grade | Big idea, emotional stakes, investors | Calm authority, intimate, mid-tempo | Strings, piano, swells | 3 to 5 s shots |
| **Kinetic manifesto** | Giant type is the visual, hard cuts on the beat, one accent colour | Bold claim, social, a punchy script | Driven, rhythmic, emphatic | Percussive, 110 to 128 BPM | Cut every 0.5 to 1.5 s |
| **Product reveal** | Clean light background, macro detail, smooth 3D or UI moves, lots of air | Software or physical product is the hero | Warm, precise, understated | Minimal electronic | Long elegant moves |
| **Premium 3D UI** | Floating 3D phones and frosted glass widgets lit like a studio, huge background type, springy pop-ins, simulated taps, live counters, match-cut transitions | The software or app is the hero and must look expensive; product sections of pitch films | Confident, crisp, minimal | Modern electronic, tight percussion | 5 to 6.5 s scenes, constant micro-motion |
| **Apple minimal product** (ref: HomeView) | Bright white space, product hero on clean ground, 3 to 6 word text cards between product shots, people only inside screens | Consumer-feeling software or hardware with a few clear benefits | Often none: music and text cards carry it | Light, rhythmic, optimistic | About 2.8 cuts per 10 s, cards cut on the beat |
| **Apple cinematic hardware** (ref: iPhone 18 Pro) | Extreme real-world proof (space, ocean, caves), macro engineering, exploded parts, thermal and blueprint views | Showing capability and engineering depth | Sparse, confident | Big cinematic build | 6+ cuts per 10 s, median shot under 1 s |
| **SaaS UI flythrough** (refs: Membrain, FCS, Madison) | Real product UI on tilted 3D planes, the camera flies continuously between panels, cursor clicks, popping notifications, avatars and faces, one brand colour plus a glow | B2B platforms; showing how the product actually works | Clear, friendly, benefit-led VO | Upbeat corporate electronic | Under 1 cut per 10 s but never still; each feature 4 to 8 s |
| **Chat-to-creation demo** (ref: Artlist x Claude) | A prompt typed live, a thinking state, then the result building on screen; warm neutral palette, centred serif lines | AI tools, agent and MCP products | Conversational, playful captions | Soft, modern | About 2.8 cuts per 10 s |
| **Hyper-kinetic AI launch** (ref: Higgsfield Katana) | Saturated colour, chromatic glitches, giant type, particles, constant zooms | Social launches, creator tools | Optional | Loud and driving (-7 LUFS) | Constant motion |
| **Data journalism** | Charts that build, maps, annotated numbers, newsroom type | The proof is numbers or a market | Clear, curious, explanatory | Light pulse, ticking | Steady, one idea per beat |
| **Founder to camera** | Founder (real footage) or AI presenter, B-roll inserts, captions | Trust, early stage, personal conviction | Real person, conversational | Low bed or none | Jump cuts, natural |
| **UGC / native social** | Phone-shot feel, vertical, captions burnt in, quick reactions | Consumer products, Reels/TikTok | Peer, casual, fast | Trending-style | Hook in 1 s, cut every 1 to 2 s |
| **Cinematic trailer** | Moody photoreal shots, title cards, speed ramps, impacts | Launches, film-related brands, hype | Trailer read, deep, dramatic pauses | Hybrid orchestral, hits, risers | Builds to a crescendo |
| **Editorial collage** | Cut-out photos, paper textures, archival mixed with graphics, stop-motion feel | Culture, history, Detroit stories, community | Storyteller, characterful | Lo-fi, soul, boom-bap | Playful, varied |
| **Isometric explainer** | Clean 3D or flat isometric worlds, systems that move, pastel or brand palette | Complex systems, platforms, B2B workflows | Friendly expert | Upbeat corporate-light | Smooth, continuous camera |
| **Whiteboard / hand-drawn** | Lines draw on, sketch notes, a hand optional | Teaching a framework, analogies | Teacherly, warm | Soft acoustic | Medium |

Styles can be blended (for example documentary footage for the emotion + data-journalism graphics for the proof), but one style leads and the other is named as an accent.

## 2b. Structure templates (learned from the reference set)

- **SaaS product film (60 to 90 s):** concrete hook in 2 s (a statistic ring, a frustrated face, a striking question) → name the pain in the customer's world (one person) → logo reveal → 3 to 5 features, each shown as one real UI moment with a click and a result → proof (integration logo ring, users, numbers from the truth table) → CTA with the URL and the logo. The logo appears 3 or more times.
- **Apple minimal:** product reveal → short text card → product in use → text card → repeat for 4 to 6 benefits → hero shot → logo.
- **Narrated thesis film (investor):** keep it to 90 s for first touch; whatever the metaphor, show the real product for at least 30% of runtime.

Universal rules from the references: one idea per text card, 3 to 7 words; show the product doing the work rather than a metaphor for it; put people (faces, avatars, hands) on screen for emotion; keep scenes bright, or dark with colour glows; transitions continue motion (fly into the next panel, morph shapes, wipes), never fade to black between ideas.

## 3. Style test before the build (the cheap gate)

For each of the two recommended directions, make a 10-second test:
- 2 to 3 style frames with `gpt_image_2_6` (about 0.75 credits each) for the hook and the turn
- the hook line read in that style's voice on `elevenlabs_v4` (about 1 credit)
- a 15 s music sketch if music carries the style (about 3 credits)

Show them side by side with the style names and what each would cost to finish. Dw picks, mixes, or redirects. Total cost of the gate: about 10 credits, against hundreds for a full build in the wrong style.

## 4. Lock the Style Spec

Write `style/spec.md` with: style name and accent style, palette (hex), type pairing, motion rules (cut rhythm, camera language, transitions), footage-to-graphics ratio, voice (engine, voice id, delivery notes, target wpm), music brief (BPM, sections with timestamps), caption treatment, and three reference frames. Every prompt, scene and mix decision cites the spec. If a later step wants to break it, ask.

## 5. Script coaching (Dw's words stay his)

Before production, read the script against the chosen style and suggest, never silently apply:
- a stronger first 3 seconds (cold open, provocative line, visual hook)
- lines that are too long for the style's pace
- places where a visual proof would beat a spoken one
- a shorter cut (60 to 90 s) when the channel calls for it
Apply only the suggestions Dw approves.

## 6. The critic pass (before Dw sees anything)

After the first full render, run a separate reviewer (a fresh agent that has not seen the build) with the spec and the cut. It scores 1 to 5 and must explain anything under 4:

| Criterion | Test |
| --- | --- |
| Hook | Would a stranger keep watching after 3 s with the sound off? |
| Style fidelity | Does every scene follow the spec? List any that drift to a default look |
| Visual variety | No more than 6 s on one composition; at least 4 distinct visual modes per minute |
| Motion quality | Springs with overshoot instead of linear or plain ease tweens; nothing simply slides in; every object has idle motion; no dead frames |
| Transitions | Designed match cuts (push into a screen, whip with blur, ripple flood, iris) instead of crossfades between unrelated shots |
| Energy curve | Does intensity build toward the turn and the close? |
| Voice conviction | Does the read sound like someone who believes it? Check wpm and emphasis on the key words |
| Clarity | Can the single job be stated after one viewing? |
| Truth | Every claim traces to the brief |

Fix every item under 4 and re-run the critic once before delivering. Tell Dw what the critic caught.

The critic also runs `attention-check` on the cut. Any metric outside its target (static frames, longest still, motion, brightness, tempo, length) counts as a score under 4.

## 7. Learn and remember

- **References:** when Dw shares a video he likes, run `watch` (or Higgsfield `video_analysis_create`), break it down into the library format above, and propose adding it as a new style row with his name for it.
- **Feedback:** every reaction ("boring", "too laid-back", "love the footage") becomes a dated rule in `style/feedback.md` and is read at the start of every project. Known rules so far: plain line art on black reads as boring; the seed_audio narrator reads as laid-back; photoreal footage and a directed ElevenLabs voice landed well.
- After each delivered video, log which style was used, the channel, and how Dw rated it, so scoring in step 2 favours what works for him.

## 8. Hand-off

Pass the Style Spec, the approved script and the test assets to `ad-engine` (or `launch-motion` / `hyperframes`). When the chosen style is **Premium 3D UI**, or a film has a product section, build those scenes with `premium-motion` and follow its storyboard gate (six full-resolution key frames approved before any animation).

Whatever the style, the motion rules from `premium-motion` apply to coded graphics: spring physics, blur-in text, idle drift and designed transitions. Those skills handle production, footage, sound and QA; this skill owns taste and direction.