"""
carousel.py — LinkedIn carousel generation via fal-ai/nano-banana-2.

Each slide is generated as a separate 1:1 image. The post is parsed into
structured slides first, then each slide gets its own nano-banana-2 call.

No Playwright. No HTML templates.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

from engine.config import BRAND_NAME
from engine.images import (
    _read_inspiration_notes,
    _build_nano_banana_prompt,
    generate_nano_banana_image,
)


@dataclass
class Slide:
    title: str
    body: str
    slide_number: int
    total_slides: int
    pillar_tag: str
    is_title_slide: bool = False
    is_cta_slide: bool = False
    step_number: int | None = None


# ---------------------------------------------------------------------------
# Post parsing
# ---------------------------------------------------------------------------

def extract_slides_from_post(post_text: str, pillar: str = "general") -> list[Slide]:
    """
    Parse a LinkedIn post into carousel slide data.
    - Slide 1: hook (first sentence) + context
    - Slides 2-N: each numbered list item
    - Final slide: CTA
    """
    # Strip YAML frontmatter
    if post_text.startswith("---"):
        parts = post_text.split("---", 2)
        post_text = parts[2].strip() if len(parts) >= 3 else post_text

    # Strip hashtags
    post_text_clean = re.sub(r"\n#\w+.*$", "", post_text, flags=re.DOTALL | re.MULTILINE).strip()

    sentences = re.split(r"(?<=[.!?])\s+", post_text_clean)
    numbered_items = re.findall(r"^\d+\.\s+(.+)$", post_text_clean, re.MULTILINE)
    pillar_label = pillar.replace("-", " ").title()

    slides: list[Slide] = []

    # Slide 1: Title / Hook
    hook = sentences[0] if sentences else post_text_clean[:150]
    hook_body = " ".join(sentences[1:3]) if len(sentences) > 1 else ""
    slides.append(Slide(
        title=hook,
        body=hook_body,
        slide_number=1,
        total_slides=0,
        pillar_tag=pillar_label,
        is_title_slide=True,
    ))

    if numbered_items:
        for i, item in enumerate(numbered_items[:6]):
            if ":" in item:
                parts = item.split(":", 1)
                title, body = parts[0].strip(), parts[1].strip()
            elif "—" in item:
                parts = item.split("—", 1)
                title, body = parts[0].strip(), parts[1].strip()
            else:
                title = item[:100]
                body = item[100:] if len(item) > 100 else ""

            slides.append(Slide(
                title=title,
                body=body,
                slide_number=len(slides) + 1,
                total_slides=0,
                pillar_tag=pillar_label,
                step_number=i + 1,
            ))
    else:
        body_sentences = sentences[3:]
        chunk_size = max(2, len(body_sentences) // 3)
        for i in range(0, min(len(body_sentences), chunk_size * 3), chunk_size):
            chunk = " ".join(body_sentences[i:i + chunk_size])
            if len(chunk.strip()) < 20:
                continue
            slides.append(Slide(
                title="",
                body=chunk,
                slide_number=len(slides) + 1,
                total_slides=0,
                pillar_tag=pillar_label,
            ))

    # Final slide: CTA
    paragraphs = [p.strip() for p in post_text_clean.split("\n\n") if p.strip()]
    cta_text = paragraphs[-1] if paragraphs else "Follow for more on AI/ML × quant finance."
    slides.append(Slide(
        title="Follow for more",
        body=cta_text[:200],
        slide_number=len(slides) + 1,
        total_slides=0,
        pillar_tag=pillar_label,
        is_cta_slide=True,
    ))

    total = len(slides)
    for s in slides:
        s.total_slides = total

    return slides


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def render_carousel(post_path: Path, output_dir: Path, pillar: str = "general") -> list[Path]:
    """
    Parse post into slides, generate each as a 1:1 PNG via nano-banana-2.
    Returns list of PNG paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    post_text = post_path.read_text()
    slides = extract_slides_from_post(post_text, pillar)
    notes = _read_inspiration_notes("carousel")

    print(f"  [carousel] Generating {len(slides)} slides via nano-banana-2...")

    paths: list[Path] = []
    for slide in slides:
        if slide.is_title_slide:
            slide_type = "title slide"
        elif slide.is_cta_slide:
            slide_type = "call-to-action slide"
        else:
            slide_type = f"content slide (point {slide.step_number})" if slide.step_number else "content slide"

        description = (
            f"LinkedIn carousel {slide_type}, slide {slide.slide_number} of {slide.total_slides}. "
            f"Title text: '{slide.title}'. "
            f"Body text: '{slide.body}'. "
            f"Topic: {slide.pillar_tag}. "
            f"Brand footer: {BRAND_NAME} | AI/ML & Quant Finance. "
            "Square format, dark background, clean layout."
        )

        prompt = _build_nano_banana_prompt(description, "carousel", pillar, notes)
        out = output_dir / f"slide-{slide.slide_number:02d}.png"
        generate_nano_banana_image(prompt, "1:1", out)
        print(f"  [carousel] Slide {slide.slide_number}/{slide.total_slides} saved.")
        paths.append(out)

    print(f"  [carousel] All slides saved to: {output_dir}")
    return paths
