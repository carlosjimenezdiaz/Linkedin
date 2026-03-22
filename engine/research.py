"""
research.py — Influencer scraping (Apify) + web trend research (Perplexity via OpenRouter).
Outputs a structured brief.md file for a given topic.
"""
import json
import time
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import requests
from openai import OpenAI

from engine.config import (
    APIFY_TOKEN,
    OPENROUTER_API_KEY,
    REPO_ROOT,
    PROFILE_DIR,
    MODEL_SYNTHESIZER,
    MODEL_RESEARCH,
)

APIFY_ACTOR = "harvestapi~linkedin-profile-posts"
APIFY_BASE = "https://api.apify.com/v2"


@dataclass
class PostSample:
    author: str
    content: str
    engagement_score: int
    posted_at: str
    hook: str  # first sentence


# ---------------------------------------------------------------------------
# Apify — LinkedIn post scraping
# ---------------------------------------------------------------------------

def _load_influencer_urls() -> list[str]:
    path = PROFILE_DIR / "influencers.json"
    data = json.loads(path.read_text())
    urls = [i["url"] if isinstance(i, dict) else i for i in data.get("influencers", [])]
    return [u for u in urls if u and not u.startswith("_")]


def _score_post(post: dict) -> int:
    eng = post.get("engagement", {}) or {}
    return (
        int(eng.get("likes", 0) or 0)
        + int(eng.get("comments", 0) or 0) * 3
        + int(eng.get("shares", 0) or 0) * 5
    )


def _parse_date(raw: str) -> datetime | None:
    """Parse ISO date string from Apify output."""
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _extract_hook(text: str) -> str:
    """Return the first sentence of the post."""
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return sentences[0][:200] if sentences else text[:200]


def _run_apify_scrape(target_urls: list[str], max_posts: int = 10) -> list[PostSample]:
    """Scrape recent posts from LinkedIn profiles via Apify."""
    if not target_urls:
        print("  [research] No influencer URLs configured — skipping LinkedIn scrape.")
        return []

    print(f"  [research] Starting Apify scrape for {len(target_urls)} profile(s)...")

    # Start run
    resp = requests.post(
        f"{APIFY_BASE}/acts/{APIFY_ACTOR}/runs",
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"},
        json={
            "targetUrls": target_urls,
            "maxPosts": max_posts,
            "includeReposts": False,
            "scrapeReactions": False,
            "scrapeComments": False,
        },
        timeout=30,
    )
    resp.raise_for_status()
    run_data = resp.json()["data"]
    run_id = run_data["id"]
    dataset_id = run_data["defaultDatasetId"]

    # Poll until complete
    for attempt in range(30):  # max 150 seconds
        time.sleep(5)
        status_resp = requests.get(
            f"{APIFY_BASE}/actor-runs/{run_id}",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}"},
            timeout=15,
        )
        status = status_resp.json()["data"]["status"]
        print(f"  [research] Apify run status: {status} (attempt {attempt + 1})")
        if status == "SUCCEEDED":
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run {run_id} ended with status: {status}")

    # Fetch results
    items_resp = requests.get(
        f"{APIFY_BASE}/datasets/{dataset_id}/items",
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"},
        params={"format": "json"},
        timeout=30,
    )
    items_resp.raise_for_status()
    items = items_resp.json()

    # Filter to last 30 days and score
    cutoff = datetime.now().astimezone() - timedelta(days=30)
    samples = []
    for item in items:
        posted_raw = (item.get("postedAt") or {}).get("date") or item.get("postedAt", "")
        posted_dt = _parse_date(str(posted_raw))
        if posted_dt and posted_dt < cutoff:
            continue

        content = item.get("content") or item.get("text") or ""
        if not content:
            continue

        author = (item.get("author") or {}).get("name") or "Unknown"
        samples.append(PostSample(
            author=author,
            content=content[:1000],
            engagement_score=_score_post(item),
            posted_at=str(posted_raw)[:10],
            hook=_extract_hook(content),
        ))

    # Sort by engagement, return top 5
    samples.sort(key=lambda p: p.engagement_score, reverse=True)
    print(f"  [research] Found {len(samples)} posts, keeping top 5.")
    return samples[:5]


# ---------------------------------------------------------------------------
# Perplexity — Web trend research via OpenRouter
# ---------------------------------------------------------------------------

def _run_perplexity_research(topic: str) -> str:
    """Use Perplexity via OpenRouter to research current trends for the topic."""
    print(f"  [research] Running Perplexity web research for: {topic}")
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
    response = client.chat.completions.create(
        model=MODEL_RESEARCH,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a research assistant for a LinkedIn content strategist "
                    "specializing in AI/ML and quantitative finance. Be specific, cite sources, "
                    "use real data."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Research current trends and practitioner discussions about: {topic}\n\n"
                    "Return exactly:\n"
                    "1. Three key recent developments (with approximate dates)\n"
                    "2. One active controversy or debate in the field\n"
                    "3. Two specific data points or statistics with their sources\n\n"
                    "Be concise and factual. No fluff."
                ),
            },
        ],
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Brief synthesis — Claude haiku summarizes findings into actionable angles
# ---------------------------------------------------------------------------

def _synthesize_brief(topic: str, posts: list[PostSample], web_research: str) -> str:
    """Use Claude haiku to synthesize research into a brief for Carlos."""
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )

    style = (REPO_ROOT / "profile" / "style.md").read_text()
    topics_md = (REPO_ROOT / "profile" / "topics.md").read_text()

    posts_section = ""
    if posts:
        posts_section = "## Top LinkedIn Posts by Engagement\n"
        for p in posts:
            posts_section += f"- **{p.author}** (score: {p.engagement_score}): \"{p.hook}\"\n"
    else:
        posts_section = "## Top LinkedIn Posts\n(No influencer data — influencers.json is empty)\n"

    response = client.chat.completions.create(
        model=MODEL_SYNTHESIZER,
        messages=[
            {
                "role": "system",
                "content": (
                    "You help Carlos Jimenez Diaz, an AI/ML engineer and quant finance professional, "
                    "find the best angle for his LinkedIn posts. He writes direct, technical, "
                    "practitioner-focused content. No buzzwords, no fluff."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Topic: {topic}\n\n"
                    f"{posts_section}\n\n"
                    f"## Web Research\n{web_research}\n\n"
                    f"## Carlos's Content Pillars\n{topics_md}\n\n"
                    "Based on this research, write:\n"
                    "1. **Angle for Carlos** (2-3 sentences): What specific angle should he take "
                    "that matches his voice and will resonate with CTOs/quant practitioners?\n"
                    "2. **Suggested Post Concepts** (2-3 options with type): e.g. "
                    "'The 3 failure modes of X — type: thought-leadership'\n\n"
                    "Keep it sharp. No generic suggestions."
                ),
            },
        ],
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def build_brief(topic: str, output_dir: Path) -> Path:
    """
    Run full research pipeline for a topic and write brief.md.
    Returns path to the brief file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Scrape LinkedIn influencer posts
    influencer_urls = _load_influencer_urls()
    posts = _run_apify_scrape(influencer_urls)

    # 2. Perplexity web research
    web_research = _run_perplexity_research(topic)

    # 3. Synthesize into brief
    print("  [research] Synthesizing brief...")
    synthesis = _synthesize_brief(topic, posts, web_research)

    # 4. Write brief.md
    today = datetime.now().strftime("%Y-%m-%d")
    posts_block = ""
    if posts:
        posts_block = "\n".join(
            f"- **{p.author}** (engagement: {p.engagement_score}): \"{p.hook}\""
            for p in posts
        )
    else:
        posts_block = "_No influencer data — add profiles to profile/influencers.json_"

    brief_content = f"""---
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

    brief_path = output_dir / "brief.md"
    brief_path.write_text(brief_content)
    print(f"  [research] Brief written to: {brief_path}")
    return brief_path
