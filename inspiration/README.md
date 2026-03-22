# Inspiration Library

This folder is your visual reference bank. Drop screenshots of LinkedIn posts here whenever you see a format, layout, or design worth replicating.

The engine doesn't read this folder automatically — it's your curation space. When you want to replicate a style, reference it when prompting Claude.

---

## Folders

### `single-image/`
Single hero images that accompany thought-leadership posts.
- What to save: images with strong composition, abstract data viz, clean brand colors
- Note what worked: lighting style, color palette, level of abstraction

### `infographics/`
Text-in-image designs — stats, numbered frameworks, bold quotes.
- What to save: infographics where text is legible and layout is clean
- Note: Ideogram generates these. Better prompts = better output.
- Include notes on the text layout (title position, body columns, footer style)

### `carousels/`
Multi-slide carousel screenshots.
- What to save: full carousel sequences (screenshot all slides)
- Note: slide count, title slide format, whether they use step numbers or icons
- Good sources: technical educators, quant finance practitioners

---

## How to Use This When Generating

When running the engine, you can reference a specific inspiration format:

```bash
# Reference an infographic style you liked
python -m engine.orchestrator --topic "data leakage" --image infographic
# Then: edit the prompt in engine/images.py → build_image_prompt() to match the style
```

For carousel design tweaks: edit `engine/templates/carousel_base.html` — all CSS variables are at the top.

---

## High-Signal Accounts to Watch (AI × Finance)

Add accounts here as you find them. These are sources of format inspiration, not content to copy.

| Account | Why interesting | Best format they use |
|---|---|---|
| (add yours) | | |
