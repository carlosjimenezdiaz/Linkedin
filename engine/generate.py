"""
generate.py — Post copy generation via Claude (through OpenRouter).
Reads brief + profile files, writes post.md with YAML frontmatter.
"""
import re
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from engine.config import (
    OPENROUTER_API_KEY,
    REPO_ROOT,
    PROFILE_DIR,
    TEMPLATES_DIR,
    PUBLISHED_DIR,
    DRAFTS_DIR,
    MODEL_WRITER,
)

_POST_TYPES = ("thought-leadership", "story", "news", "cta")


def _load_recent_published(n: int = 3) -> str:
    """Load the n most recent published posts as voice grounding examples."""
    posts = sorted(PUBLISHED_DIR.glob("**/*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not posts:
        return "(No published posts yet — using style guide as sole reference)"

    excerpts = []
    for post_path in posts[:n]:
        text = post_path.read_text()
        # Strip YAML frontmatter
        if text.startswith("---"):
            parts = text.split("---", 2)
            text = parts[2].strip() if len(parts) >= 3 else text
        excerpts.append(f"--- Example post ---\n{text[:600]}")
    return "\n\n".join(excerpts)


def _infer_image_type(post_type: str, post_text: str) -> str:
    """Infer best image type from post structure."""
    # Carousel if there's a numbered list with 3+ items
    numbered = re.findall(r"^\d+\.", post_text, re.MULTILINE)
    if len(numbered) >= 3:
        return "carousel"
    # Infographic if there are stats or data points
    if re.search(r"\d+%|\$\d+|\d+x\b", post_text):
        return "infographic"
    return "diagram"


def generate_post(brief_path: Path, post_type: str, slug: str) -> tuple[Path, str]:
    """
    Generate a LinkedIn post from a research brief.
    Returns (path_to_post_md, inferred_image_type).
    """
    if post_type not in _POST_TYPES:
        raise ValueError(f"post_type must be one of {_POST_TYPES}, got: {post_type}")

    # Load context
    style = (PROFILE_DIR / "style.md").read_text()
    audience = (PROFILE_DIR / "audience.md").read_text()
    template_path = TEMPLATES_DIR / f"{post_type}.md"
    if not template_path.exists():
        template_path = TEMPLATES_DIR / "thought-leadership.md"
    template = template_path.read_text()
    brief = brief_path.read_text()
    recent_posts = _load_recent_published()

    print(f"  [generate] Writing post (model: {MODEL_WRITER})...")

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )

    system_prompt = f"""You are Carlos Jimenez Diaz's LinkedIn ghostwriter. You write exactly in his voice.

VOICE & STYLE RULES (follow strictly):
{style}

TARGET AUDIENCE:
{audience}

RECENT PUBLISHED POSTS (Carlos's actual voice, match this exactly):
{recent_posts}

Rules:
- 150-300 words. Never under 100, never over 350.
- Strong hook as the first line, standalone sentence that works alone.
- No buzzwords: no "game-changing", "revolutionary", "disruptive", "in today's fast-paced world"
- No "I'm excited/humbled/proud to share"
- End with a natural CTA, never "like and share"
- 3-5 hashtags at the very end on their own line
- Output ONLY the post text. No explanation, no preamble.

ANTI-AI DETECTION (CRITICAL, follow every rule):
- NEVER use em dashes. Not once. Use periods, commas, or start a new sentence.
- NEVER use numbered lists or bold section headers in the post.
- NEVER write with parallel structure. Each paragraph should flow differently. Vary sentence length and rhythm.
- NEVER use these AI-tell words: "leverage", "streamline", "optimize", "actionable", "unlock", "the real value", "infrastructure" in polished essay style.
- USE contractions everywhere. Write casual: "annoying as hell", "honestly that alone was worth it."
- START some sentences with "Look," "So," "But," "And" like real speech.
- DO NOT follow intro-body-conclusion format. Just start talking and end with an opinion.
- Make it human-messy. Uneven paragraphs. Occasional fragments. The way someone types fast without heavy editing."""

    user_prompt = f"""Write a LinkedIn post using the template structure and research brief below.

TEMPLATE STRUCTURE:
{template}

RESEARCH BRIEF:
{brief}

Post type: {post_type}

Write the complete post now."""

    response = client.chat.completions.create(
        model=MODEL_WRITER,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=700,
    )

    post_text = response.choices[0].message.content.strip()

    # Count words
    word_count = len(post_text.split())
    print(f"  [generate] Post generated: {word_count} words")

    # Infer image type
    image_type = _infer_image_type(post_type, post_text)

    # Extract topic from brief for frontmatter
    topic_match = re.search(r'topic:\s*"([^"]+)"', brief)
    topic = topic_match.group(1) if topic_match else slug.replace("-", " ")

    # Build YAML frontmatter
    today = datetime.now().strftime("%Y-%m-%d")
    pillar = _infer_pillar(post_text)
    frontmatter = f"""---
type: {post_type}
pillar: {pillar}
status: draft
topic: "{topic}"
slug: {slug}
created: {today}
word_count: {word_count}
image_type: {image_type}
scheduled: null
posted_url: null
---

"""

    # Write post.md
    draft_dir = DRAFTS_DIR / slug
    draft_dir.mkdir(parents=True, exist_ok=True)
    post_path = draft_dir / "post.md"
    post_path.write_text(frontmatter + post_text)
    print(f"  [generate] Post written to: {post_path}")

    return post_path, image_type


def _infer_pillar(post_text: str) -> str:
    """Roughly infer which content pillar the post belongs to."""
    text_lower = post_text.lower()
    if any(w in text_lower for w in ["agent", "agentic", "llm agent", "autonomous"]):
        return "agentic-ai"
    if any(w in text_lower for w in ["feature engineering", "mlops", "model deployment", "data leakage"]):
        return "traditional-ml"
    if any(w in text_lower for w in ["portfolio", "quant", "trading", "alpha", "asset management"]):
        return "wealth-asset-management"
    if any(w in text_lower for w in ["risk", "regulatory", "compliance", "sr 11-7", "model risk"]):
        return "risk-management"
    return "general"
