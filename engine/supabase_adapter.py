"""
engine/supabase_adapter.py — Wraps existing engine functions with:
  1. Progress callbacks for SSE updates
  2. Supabase DB writes (dual-write: disk + Supabase)
  3. Supabase Storage uploads for images

The core engine functions are NOT modified. This adapter calls them,
captures their outputs, and writes to Supabase alongside disk.
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from engine.config import DRAFTS_DIR, REPO_ROOT
from engine.packager import make_slug


ProgressCallback = Callable[[str, str, int], None]


def _noop_progress(phase: str, message: str, pct: int) -> None:
    """Default no-op progress callback."""
    pass


# ---------------------------------------------------------------------------
# Phase 1: Research → Brief
# ---------------------------------------------------------------------------

def run_research(
    topic: str,
    slug: str,
    on_progress: ProgressCallback = _noop_progress,
) -> dict:
    """
    Run the research pipeline. Writes brief to disk AND returns data for Supabase.
    Returns dict with keys: brief_path, topic, influencer_posts, web_research, synthesis, full_brief_md
    """
    from engine.research import (
        _load_influencer_urls,
        _run_apify_scrape,
        _run_perplexity_research,
        _synthesize_brief,
        build_brief,
    )

    draft_dir = DRAFTS_DIR / slug
    draft_dir.mkdir(parents=True, exist_ok=True)

    on_progress("research", "Loading influencer URLs...", 5)
    influencer_urls = _load_influencer_urls()

    on_progress("research", f"Scraping {len(influencer_urls)} LinkedIn profiles via Apify...", 10)
    posts = _run_apify_scrape(influencer_urls)
    influencer_data = [
        {
            "author": p.author,
            "content": p.content,
            "engagement_score": p.engagement_score,
            "posted_at": p.posted_at,
            "hook": p.hook,
        }
        for p in posts
    ]

    on_progress("research", "Running Perplexity web research...", 40)
    web_research = _run_perplexity_research(topic)

    on_progress("research", "Synthesizing brief with Claude...", 60)
    synthesis = _synthesize_brief(topic, posts, web_research)

    # Build and write brief.md to disk (keeps CLI working)
    on_progress("research", "Writing brief to disk...", 70)
    today = datetime.now().strftime("%Y-%m-%d")
    posts_block = ""
    if posts:
        posts_block = "\n".join(
            f'- **{p.author}** (engagement: {p.engagement_score}): "{p.hook}"'
            for p in posts
        )
    else:
        posts_block = "_No influencer data — add profiles to profile/influencers.json_"

    full_brief_md = f"""---
topic: "{topic}"
researched_at: "{today}"
sources: apify+perplexity+claude
---

## What's Getting Engagement (LinkedIn Influencers)
{posts_block}

## Web Research (Perplexity)
{web_research}

## Analysis & Angles for Carlos
{synthesis}
"""
    brief_path = draft_dir / "brief.md"
    brief_path.write_text(full_brief_md)

    on_progress("research", "Research complete.", 75)

    return {
        "brief_path": brief_path,
        "topic": topic,
        "influencer_posts": influencer_data,
        "web_research": web_research,
        "synthesis": synthesis,
        "full_brief_md": full_brief_md,
    }


# ---------------------------------------------------------------------------
# Phase 2: Write → Post
# ---------------------------------------------------------------------------

def run_write(
    brief_path: Path,
    post_type: str,
    slug: str,
    on_progress: ProgressCallback = _noop_progress,
) -> dict:
    """
    Run the writing phase. Writes post.md to disk AND returns data for Supabase.
    Returns dict with keys: post_path, body, word_count, pillar, image_type, topic
    """
    from engine.generate import generate_post, _infer_pillar

    on_progress("write", "Generating post with Claude Sonnet...", 80)
    post_path, inferred_image_type = generate_post(brief_path, post_type, slug)

    # Parse the written file to extract body and metadata
    post_text = post_path.read_text()
    body = post_text
    if post_text.startswith("---"):
        parts = post_text.split("---", 2)
        if len(parts) >= 3:
            body = parts[2].strip()

    word_count = len(body.split())
    pillar = _infer_pillar(body)

    # Extract topic from brief
    brief_text = brief_path.read_text()
    topic_match = re.search(r'topic:\s*"([^"]+)"', brief_text)
    topic = topic_match.group(1) if topic_match else slug.replace("-", " ")

    on_progress("write", f"Post generated: {word_count} words.", 85)

    return {
        "post_path": post_path,
        "body": body,
        "word_count": word_count,
        "pillar": pillar,
        "image_type": inferred_image_type,
        "topic": topic,
    }


# ---------------------------------------------------------------------------
# Phase 3: Image generation
# ---------------------------------------------------------------------------

def run_images(
    post_path: Path,
    image_type: str,
    slug: str,
    pillar: str = "general",
    on_progress: ProgressCallback = _noop_progress,
) -> list[dict]:
    """
    Generate images. Writes to disk AND returns data for Supabase upload.
    Returns list of dicts with keys: local_path, image_type, slide_number, prompt
    """
    draft_dir = DRAFTS_DIR / slug
    images_dir = draft_dir / "images"
    results = []

    if image_type == "none":
        on_progress("image", "Skipping image generation.", 100)
        return results

    if image_type == "carousel":
        from engine.carousel import render_carousel
        on_progress("image", "Generating carousel slides...", 90)
        paths = render_carousel(post_path, images_dir / "carousel", pillar)
        for i, p in enumerate(paths):
            results.append({
                "local_path": p,
                "image_type": "carousel",
                "slide_number": i + 1,
                "prompt": None,
            })
    else:
        from engine.images import generate_image
        on_progress("image", f"Generating {image_type} image...", 90)
        paths = generate_image(post_path, image_type, images_dir, pillar)
        for p in paths:
            results.append({
                "local_path": p,
                "image_type": image_type,
                "slide_number": None,
                "prompt": None,
            })

    on_progress("image", f"Generated {len(results)} image(s).", 95)
    return results


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def run_full_pipeline(
    topic: str,
    post_type: str = "thought-leadership",
    image_type: str = "auto",
    idea_id: Optional[str] = None,
    on_progress: ProgressCallback = _noop_progress,
) -> dict:
    """
    Run the complete 3-phase pipeline.
    Returns all data needed to persist to Supabase.
    """
    from api import db
    from api.storage import upload_image

    slug = make_slug(topic)

    # Phase 1: Research
    on_progress("research", "Starting research phase...", 0)
    research_data = run_research(topic, slug, on_progress)

    # Save brief to Supabase
    brief_row = db.create_brief(
        topic=topic,
        influencer_posts=research_data["influencer_posts"],
        web_research=research_data["web_research"],
        synthesis=research_data["synthesis"],
        full_brief_md=research_data["full_brief_md"],
        idea_id=idea_id,
    )

    # Phase 2: Write
    on_progress("write", "Starting writing phase...", 75)
    write_data = run_write(research_data["brief_path"], post_type, slug, on_progress)

    # Resolve image type
    resolved_image_type = image_type
    if resolved_image_type == "auto":
        resolved_image_type = write_data["image_type"]

    # Save post to Supabase
    post_row = db.create_post(
        slug=slug,
        topic=topic,
        post_type=post_type,
        pillar=write_data["pillar"],
        body=write_data["body"],
        word_count=write_data["word_count"],
        image_type=resolved_image_type,
        brief_id=brief_row["id"],
        idea_id=idea_id,
    )

    # Update idea status if linked
    if idea_id:
        db.update_idea(idea_id, {"status": "drafted"})

    # Phase 3: Images
    on_progress("image", "Starting image generation...", 85)
    image_results = run_images(
        write_data["post_path"], resolved_image_type, slug, write_data["pillar"], on_progress
    )

    # Upload images to Supabase Storage and save records
    for img in image_results:
        storage_path = f"{slug}/{img['local_path'].name}"
        public_url = upload_image(img["local_path"], storage_path)
        db.create_image(
            post_id=post_row["id"],
            image_type=img["image_type"],
            storage_path=storage_path,
            public_url=public_url,
            prompt=img.get("prompt"),
            slide_number=img.get("slide_number"),
        )

    on_progress("complete", "Pipeline complete!", 100)

    return {
        "post_id": post_row["id"],
        "brief_id": brief_row["id"],
        "slug": slug,
        "post": post_row,
        "brief": brief_row,
    }


def run_research_only(
    topic: str,
    idea_id: Optional[str] = None,
    on_progress: ProgressCallback = _noop_progress,
) -> dict:
    """Run research phase only, save brief to Supabase."""
    from api import db

    slug = make_slug(topic)

    on_progress("research", "Starting research phase...", 0)
    research_data = run_research(topic, slug, on_progress)

    brief_row = db.create_brief(
        topic=topic,
        influencer_posts=research_data["influencer_posts"],
        web_research=research_data["web_research"],
        synthesis=research_data["synthesis"],
        full_brief_md=research_data["full_brief_md"],
        idea_id=idea_id,
    )

    on_progress("complete", "Research complete!", 100)

    return {
        "brief_id": brief_row["id"],
        "brief": brief_row,
    }
