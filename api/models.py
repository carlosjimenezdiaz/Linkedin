"""
api/models.py — Pydantic models for request/response schemas.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------------
# Ideas
# ---------------------------------------------------------------------------

class IdeaCreate(BaseModel):
    title: str
    post_type: str = "thought-leadership"
    pillar: Optional[str] = None
    theme: Optional[str] = None


class IdeaUpdate(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    pillar: Optional[str] = None


class IdeaOut(BaseModel):
    id: str
    number: int
    title: str
    post_type: str
    pillar: Optional[str]
    theme: Optional[str]
    status: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------

class PostUpdate(BaseModel):
    body: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    posted_url: Optional[str] = None


class PostOut(BaseModel):
    id: str
    brief_id: Optional[str]
    idea_id: Optional[str]
    slug: str
    topic: str
    post_type: str
    pillar: str
    status: str
    body: str
    word_count: int
    image_type: Optional[str]
    scheduled_at: Optional[datetime]
    posted_url: Optional[str]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Briefs
# ---------------------------------------------------------------------------

class BriefOut(BaseModel):
    id: str
    idea_id: Optional[str]
    topic: str
    influencer_posts: Optional[list | dict] = None
    web_research: Optional[str]
    synthesis: Optional[str]
    full_brief_md: Optional[str]
    researched_at: datetime


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------

class ImageOut(BaseModel):
    id: str
    post_id: str
    image_type: str
    storage_path: str
    public_url: Optional[str]
    prompt: Optional[str]
    slide_number: Optional[int]
    created_at: datetime


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class PipelineRequest(BaseModel):
    topic: str
    post_type: str = "thought-leadership"
    image_type: str = "auto"
    idea_id: Optional[str] = None


class PipelineRunOut(BaseModel):
    id: str
    post_id: Optional[str]
    idea_id: Optional[str]
    run_type: str
    status: str
    current_phase: Optional[str]
    progress_pct: int
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]


class WriteRequest(BaseModel):
    brief_id: str
    post_type: str = "thought-leadership"
    image_type: str = "auto"


class ImageRequest(BaseModel):
    post_id: str
    image_type: str = "auto"
