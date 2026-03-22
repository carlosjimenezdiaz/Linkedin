"""
images.py — Image generation via fal-ai/nano-banana-2.

All image types (diagram, branded, infographic) go through one pipeline:
  1. Claude haiku writes a content-specific visual description from the post
  2. Python builds the final prompt (brand palette + description + inspiration notes)
  3. fal-ai/nano-banana-2 generates the image

No Playwright. No Ideogram. No fal.ai/Flux.
"""
import os
import re
from pathlib import Path

import requests
from openai import OpenAI

from engine.config import (
    FAL_KEY,
    OPENROUTER_API_KEY,
    BRAND_BG_COLOR,
    BRAND_ACCENT_COLOR,
    BRAND_NAME,
    INSPIRATION_DIR,
    MODEL_SYNTHESIZER,
    NANO_BANANA_MODEL,
)

# fal_client reads FAL_KEY from env
os.environ.setdefault("FAL_KEY", FAL_KEY)

_PILLAR_ACCENT = {
    "agentic-ai":              "#4a9eff",
    "traditional-ml":          "#c9a84c",
    "wealth-asset-management": "#50c878",
    "risk-management":         "#e05c5c",
    "general":                 "#c9a84c",
}

_INSPIRATION_FOLDER = {
    "branded":     "single-image",
    "diagram":     "infographics",
    "infographic": "infographics",
    "carousel":    "carousels",
}

_ASPECT_RATIO = {
    "diagram":     "16:9",
    "branded":     "16:9",
    "infographic": "1:1",
    "carousel":    "1:1",
}

_STYLE_DIRECTION = {
    "diagram": (
        "Clean professional technical diagram. Workflow chart or framework visualization. "
        "Labeled boxes connected by arrows. Clear hierarchy. No decorative elements."
    ),
    "branded": (
        "Professional digital illustration. Abstract concept visualization. "
        "Atmospheric, cinematic. No literal people. No stock-photo feel."
    ),
    "infographic": (
        "Clean infographic layout. Key statistics and numbered insights. "
        "Bold typography. High contrast. Data visualization aesthetic."
    ),
    "carousel": (
        "LinkedIn carousel slide. Single focused concept per slide. "
        "Bold title, short supporting text. Clean minimal layout."
    ),
}


# ---------------------------------------------------------------------------
# Inspiration notes reader
# ---------------------------------------------------------------------------

def _read_inspiration_notes(image_type: str) -> str:
    """Read notes.md from the relevant inspiration subfolder. Returns '' if missing/empty."""
    subfolder = _INSPIRATION_FOLDER.get(image_type, "infographics")
    notes_path = INSPIRATION_DIR / subfolder / "notes.md"
    if not notes_path.exists():
        return ""
    content = notes_path.read_text().strip()
    # Strip comment lines (lines starting with #)
    active_lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
    return "\n".join(active_lines).strip()


# ---------------------------------------------------------------------------
# Claude visual description
# ---------------------------------------------------------------------------

_DESCRIPTION_SYSTEM = """\
You are a visual art director for a LinkedIn content engine.
Given a LinkedIn post and an image type, write a precise 3-5 sentence visual description
of what the image should show. Be specific to the post content — reference the actual
concepts, frameworks, or data points in the post. No generic descriptions.

Return only the visual description. No preamble, no explanation."""

_DESCRIPTION_USER = """\
Post:
{post_text}

Image type: {image_type}
Content pillar: {pillar}

Describe exactly what this image should show. Be concrete and specific to this post's content."""


def _ask_claude_visual_description(post_text: str, image_type: str, pillar: str) -> str:
    """Claude haiku returns a content-specific visual description for nano-banana-2."""
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
    response = client.chat.completions.create(
        model=MODEL_SYNTHESIZER,
        messages=[
            {"role": "system", "content": _DESCRIPTION_SYSTEM},
            {"role": "user", "content": _DESCRIPTION_USER.format(
                post_text=post_text[:1500],
                image_type=image_type,
                pillar=pillar,
            )},
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_nano_banana_prompt(
    description: str,
    image_type: str,
    pillar: str,
    inspiration_notes: str,
) -> str:
    """Assemble the final prompt for nano-banana-2."""
    accent = _PILLAR_ACCENT.get(pillar, _PILLAR_ACCENT["general"])
    style = _STYLE_DIRECTION.get(image_type, _STYLE_DIRECTION["branded"])

    parts = [
        f"Dark navy background ({BRAND_BG_COLOR}). Accent color: {accent}. Brand: {BRAND_NAME} | AI/ML & Quant Finance.",
        style,
        description,
    ]

    if inspiration_notes:
        parts.append(f"Style reference: {inspiration_notes}")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# nano-banana-2 image generation
# ---------------------------------------------------------------------------

def generate_nano_banana_image(prompt: str, aspect_ratio: str, output_path: Path) -> Path:
    """Call fal-ai/nano-banana-2, download result to output_path."""
    try:
        import fal_client
    except ImportError:
        raise ImportError("fal-client not installed. Run: pip install fal-client")

    print(f"  [images] Generating via {NANO_BANANA_MODEL} (aspect: {aspect_ratio})...")
    result = fal_client.subscribe(
        NANO_BANANA_MODEL,
        arguments={
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": "1K",
            "output_format": "png",
        },
    )
    image_url = result["images"][0]["url"]
    _download_image(image_url, output_path)
    print(f"  [images] Saved: {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------

def generate_image(
    post_path: Path,
    image_type: str,
    output_dir: Path,
    pillar: str = "general",
) -> list[Path]:
    """
    Generate an image for a post using nano-banana-2.
    Returns list of generated image paths.
    For carousel, delegates to carousel.py (called from orchestrator).
    """
    if image_type == "carousel":
        raise ValueError("Use carousel.py directly for carousel generation.")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Strip frontmatter
    post_text = post_path.read_text()
    if post_text.startswith("---"):
        parts = post_text.split("---", 2)
        post_text = parts[2].strip() if len(parts) >= 3 else post_text

    print(f"  [images] Asking Claude for visual description...")
    description = _ask_claude_visual_description(post_text, image_type, pillar)

    notes = _read_inspiration_notes(image_type)
    if notes:
        print(f"  [images] Injecting inspiration notes ({len(notes.splitlines())} line(s)).")

    prompt = _build_nano_banana_prompt(description, image_type, pillar, notes)
    aspect = _ASPECT_RATIO.get(image_type, "16:9")
    out = output_dir / f"{image_type}.png"

    return [generate_nano_banana_image(prompt, aspect, out)]


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _download_image(url: str, path: Path) -> None:
    """Download image from URL to local path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with open(path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
