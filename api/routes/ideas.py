"""
api/routes/ideas.py — Ideas CRUD endpoints.
"""
from fastapi import APIRouter, HTTPException
from api.models import IdeaCreate, IdeaUpdate, IdeaOut
from api import db

router = APIRouter(prefix="/api/ideas", tags=["ideas"])


@router.get("")
async def list_ideas(status: str = None):
    """List all ideas, optionally filtered by status."""
    return db.list_ideas(status=status)


@router.post("")
async def create_ideas(ideas: list[IdeaCreate]):
    """Create one or more ideas."""
    created = []
    for idea in ideas:
        row = db.create_idea(
            title=idea.title,
            post_type=idea.post_type,
            pillar=idea.pillar,
            theme=idea.theme,
        )
        created.append(row)
    return created


@router.get("/{idea_id}")
async def get_idea(idea_id: str):
    """Get a single idea."""
    idea = db.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@router.patch("/{idea_id}")
async def update_idea(idea_id: str, updates: IdeaUpdate):
    """Update an idea (status, title, pillar)."""
    data = updates.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No updates provided")
    result = db.update_idea(idea_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Idea not found")
    return result
