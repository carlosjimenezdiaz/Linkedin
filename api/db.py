"""
api/db.py — Supabase CRUD operations for all tables.
"""
from datetime import datetime
from typing import Optional
from api.config import supabase


# ---------------------------------------------------------------------------
# Ideas
# ---------------------------------------------------------------------------

def get_next_idea_number() -> int:
    """Return the next available idea number."""
    result = supabase.table("ideas").select("number").order("number", desc=True).limit(1).execute()
    if result.data:
        return result.data[0]["number"] + 1
    return 1


def create_idea(title: str, post_type: str, pillar: str = None, theme: str = None) -> dict:
    number = get_next_idea_number()
    row = {
        "number": number,
        "title": title,
        "post_type": post_type,
        "pillar": pillar,
        "theme": theme,
        "status": "backlog",
    }
    result = supabase.table("ideas").insert(row).execute()
    return result.data[0]


def list_ideas(status: str = None) -> list[dict]:
    query = supabase.table("ideas").select("*").order("number")
    if status:
        query = query.eq("status", status)
    return query.execute().data


def get_idea(idea_id: str) -> Optional[dict]:
    result = supabase.table("ideas").select("*").eq("id", idea_id).execute()
    return result.data[0] if result.data else None


def update_idea(idea_id: str, updates: dict) -> dict:
    result = supabase.table("ideas").update(updates).eq("id", idea_id).execute()
    return result.data[0] if result.data else None


# ---------------------------------------------------------------------------
# Briefs
# ---------------------------------------------------------------------------

def create_brief(
    topic: str,
    influencer_posts: list = None,
    web_research: str = None,
    synthesis: str = None,
    full_brief_md: str = None,
    idea_id: str = None,
) -> dict:
    row = {
        "topic": topic,
        "influencer_posts": influencer_posts,
        "web_research": web_research,
        "synthesis": synthesis,
        "full_brief_md": full_brief_md,
        "idea_id": idea_id,
    }
    result = supabase.table("briefs").insert(row).execute()
    return result.data[0]


def get_brief(brief_id: str) -> Optional[dict]:
    result = supabase.table("briefs").select("*").eq("id", brief_id).execute()
    return result.data[0] if result.data else None


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------

def create_post(
    slug: str,
    topic: str,
    post_type: str,
    pillar: str,
    body: str,
    word_count: int,
    image_type: str = None,
    brief_id: str = None,
    idea_id: str = None,
) -> dict:
    row = {
        "slug": slug,
        "topic": topic,
        "post_type": post_type,
        "pillar": pillar,
        "body": body,
        "word_count": word_count,
        "image_type": image_type,
        "brief_id": brief_id,
        "idea_id": idea_id,
        "status": "draft",
    }
    result = supabase.table("posts").insert(row).execute()
    return result.data[0]


def list_posts(status: str = None, pillar: str = None) -> list[dict]:
    query = supabase.table("posts").select("*").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    if pillar:
        query = query.eq("pillar", pillar)
    return query.execute().data


def get_post(post_id: str) -> Optional[dict]:
    result = supabase.table("posts").select("*").eq("id", post_id).execute()
    return result.data[0] if result.data else None


def update_post(post_id: str, updates: dict) -> dict:
    if "body" in updates and updates["body"]:
        updates["word_count"] = len(updates["body"].split())
    result = supabase.table("posts").update(updates).eq("id", post_id).execute()
    return result.data[0] if result.data else None


def delete_post(post_id: str) -> bool:
    supabase.table("posts").delete().eq("id", post_id).execute()
    return True


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------

def create_image(
    post_id: str,
    image_type: str,
    storage_path: str,
    public_url: str = None,
    prompt: str = None,
    slide_number: int = None,
) -> dict:
    row = {
        "post_id": post_id,
        "image_type": image_type,
        "storage_path": storage_path,
        "public_url": public_url,
        "prompt": prompt,
        "slide_number": slide_number,
    }
    result = supabase.table("images").insert(row).execute()
    return result.data[0]


def list_images(post_id: str) -> list[dict]:
    return (
        supabase.table("images")
        .select("*")
        .eq("post_id", post_id)
        .order("slide_number")
        .execute()
        .data
    )


# ---------------------------------------------------------------------------
# Pipeline Runs
# ---------------------------------------------------------------------------

def create_pipeline_run(run_type: str, idea_id: str = None) -> dict:
    row = {
        "run_type": run_type,
        "status": "running",
        "current_phase": "starting",
        "progress_pct": 0,
        "idea_id": idea_id,
    }
    result = supabase.table("pipeline_runs").insert(row).execute()
    return result.data[0]


def update_pipeline_run(run_id: str, updates: dict) -> dict:
    result = supabase.table("pipeline_runs").update(updates).eq("id", run_id).execute()
    return result.data[0] if result.data else None


def get_pipeline_run(run_id: str) -> Optional[dict]:
    result = supabase.table("pipeline_runs").select("*").eq("id", run_id).execute()
    return result.data[0] if result.data else None
