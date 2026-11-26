---
name: "printful-tee-mockups"
description: "Make premium, Printful-accurate t-shirt mockups in Kittl for Dw's store: Black or mixed-race women models, large chest print placed below the collar, full product photo set."
---

# Printful-accurate t-shirt mockups (Kittl)

Use when Dw shares a t-shirt design and wants mockups, product photos or a photo set for the Shopify store (Custom Designs Factory). The goal is product imagery that looks like a high-end e-commerce brand AND matches what Printful will actually ship.

## Default deliverable: the 3-image product set (in this order)

Unless Dw asks for something else, every design gets exactly this set:

1. **Hero — AI-generated styled lifestyle shot.** A Black or mixed-race woman wearing the shirt, styled as a full outfit (Dw's approved reference: open black leather moto jacket worn over the tee with the print unobstructed, olive cargo pants, chunky white sneakers, small gold chain, against a textured concrete wall, late-afternoon light). Generated in Kittl with the real design file as a reference image (see "Hero generation" below).
2. **Flat lay — white tee on a clean background.** Real mockup render (template 2050) with the large print, then background removed so it sits cleanly on the store's background.
3. **Flat lay — second Printful color on a clean background.** Same render recolored to a color Printful stocks for the blank (approved default: soft **Pink** on Bella+Canvas 6400), background removed. This image is attached to that color variant in Shopify.

Optional extras only when asked: extra lifestyle templates, hanger shot, "one tee, three ways" styling carousel (everyday / street / dressed-up), editorial campaign image for ads.

## Standing rules (apply every time without being asked)

1. **Models: Black or mixed-race women.** Every on-model image uses a Black or mixed-race woman. Include body-type variety (e.g. one curvy/plus model) across extras.
2. **Garment must match a Printful blank.** Default product: Bella+Canvas 6400 Women's Relaxed T-Shirt (crew neck, relaxed fit, normal hip length). Unisex option: Bella+Canvas 3001 (crew neck). Only use plain crew-neck, short-sleeve tees with normal length. REJECT scoop/U-neck, V-neck, cropped or knotted hems, oversized boxy drop-shoulder cuts, or long sleeves — unless Dw says he is listing that specific Printful product. In AI generation prompts, state the crew neck, relaxed fit and "not cropped, not oversized" explicitly.
3. **Print size: large and bold.** Near Printful's max front print width (about 12 in). In Kittl placement terms usually maxSize ≈ 0.35–0.42 depending on framing (design width ~55–60% of the visible chest width). Never shrink to a small chest logo unless asked. Never exceed what a 12 in x 16 in print area could physically produce (e.g. not sleeve seam to sleeve seam).
4. **Print position: below the collar.** Top edge of the design sits about 3 in below the collar seam — clearly separated from the neckline, never touching or tucked under it. If the first render looks close to the neck, move centerY down (typically +0.04 to +0.05) and re-render.
5. **Fully visible.** visibleRatio must be 1.0 — nothing cut off by the neckline, arms, jacket, bag straps, hair or frame edge.
6. **Consistency across the set.** Same relative print size and position on every image so shoppers don't see different print sizes.
7. **Shirt color must suit the design.** Dark-lettered designs → white/cream/sand/pink tees. Light/cream-lettered designs → black/brown tees. Only offer colors Printful stocks for the chosen blank, and tell Dw to confirm the color exists in Printful's color picker for that blank.

## Workflow

1. **Get the design into Kittl.** Direct uploads from the workspace are blocked by the network allowlist, so open `kittl-open-image-uploader` and ask Dw to drop the design(s) in. Use `kittl-view-image` on the returned objectId to confirm which design it is, and use the image URL it reports (`https://cache.kittl.com/pr:sharp/plain/api/users/<team>/uploads/<id>.png`) as the design input everywhere (the bare objectId can 404 in renders).
2. **Workspace:** `kittl-list-teams` → default team id (currently `clx1my61w01ovws1jbuocuqph`). Dw has Kittl Pro, so premium templates and paid models are available. Check `kittl-get-token-balance` before generating.

### Hero generation (image 1)

- Tool: `kittl-generate-media`, type image, model **GPT Image 2.5 Sunburst-HQ** (`cmu0vp9fee5hg0j80zsa0tj58`, ~20 tokens), aspect ratio **4:5**.
- `referenceImages`: the design URL (plus a previously approved model image first, when keeping the same face across images).
- Prompt must include: photorealistic premium lookbook photo; the woman's description; plain white short-sleeve crew-neck relaxed women's tee, normal hip length, not cropped/oversized; "the reference graphic printed large on the center chest exactly as provided — identical lettering, spelling, colors and layout"; ~11 in wide; top ~3 in below the collar; fully visible (any jacket worn open); the outfit and setting; framing (head to knees), lens and light.
- Poll `kittl-get-media-generation-status`, then `kittl-view-image` to check neckline, fit, print size and position.
- Always tell Dw to zoom in at full size and verify the small lettering — AI can warp fine text. If wording is off, fix it by pasting the real design over the chest in Kittl's editor. Avoid invented background text/signage where possible.
- AI-generated model images used in TikTok/Meta ads should carry the platform's AI-generated label.

### Flat lays (images 2 and 3)

- `kittl-render-mockup`, template **2050** (women's flat lay), size 1080, placement centerX 0.502, centerY 0.42, maxSize 0.42.
- White: no backgroundColor. Pink: `backgroundColor: "#ffc7c9"` (warm soft pink; #f5cfd8 reads lilac). Other colors: pick a hex close to the Printful swatch and re-tint if it reads off.
- Then `kittl-remove-image-background` with mode **enhanced** on each render for a clean transparent background (the template is shot on concrete).
- Note to Dw: recolors are digital approximations — compare against the first Printful sample and re-tint if needed.

### Other templates (extras only)

`kittl-search-mockup-templates` does not filter by model ethnicity or neckline, so `kittl-view-image` each preview and apply rules 1–2.
- Known good crew-neck templates with Black/mixed-race women (placement centerX / centerY / maxSize): **16564** city street, sunglasses (0.515 / 0.725 / 0.37); **16708** curvy woman at home with mug (0.5 / 0.525 / 0.37); **1448** natural curls, bedroom (0.494 / 0.735 / 0.34); **1449** afro, draped backdrop (0.508 / 0.745 / 0.32); **2801** editorial dark studio — campaign/ads only, shirt partly in frame.
- Hanger: **1444** (0.49 / 0.41 / 0.30) — collection-grid hover image.
- Rejected: **1450** (scoop neck, knotted crop — doesn't match Printful blank).
- Check every render: size (rule 3), collar gap (rule 4), visibleRatio (rule 5). Re-render until all pass before showing Dw.

### Finish

- Renders expire in ~24h: `kittl-save-image-to-library` with the render's objectId and a clear name (`<Design> - <Scene> (final)`). Generated images and background-removal results are already library uploads (saving them returns OBJECT_NOT_FOUND — that's fine).
- `kittl-upscale-image` each final; poll `kittl-get-image-upscale-status` until COMPLETE.

## Report back

Briefly: the 3 images in order, the Printful blank and colors to list (e.g. Bella+Canvas 6400 in White + Pink), which image goes on which color variant, and anything to verify (lettering on the AI hero, Printful color availability, recolor accuracy). Remind Dw to export finals as 2048×2048 from Kittl's editor for Shopify, and that a higher-resolution source design is needed for a print close-up.

## Store context

- Store: Custom Designs Factory (Shopify), stealth-brand positioning — product names stand alone (no references to viral videos or real people).
- New drops get the `just-dropped` tag so they appear in the "Just Dropped" smart collection.
- Products must be created through Printful so orders fulfill automatically; after that, rename/tag them in Shopify and attach the color flat lay to its variant.