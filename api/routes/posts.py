"""
api/routes/posts.py — Posts CRUD endpoints.
"""
from fastapi import APIRouter, HTTPException
from api.models import PostUpdate, PostOut
from api import db

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("")
async def list_posts(status: str = None, pillar: str = None):
    """List all posts, optionally filtered by status and/or pillar."""
    return db.list_posts(status=status, pillar=pillar)


@router.get("/{post_id}")
async def get_post(post_id: str):
    """Get a single post with its brief and images."""
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Attach related data
    images = db.list_images(post_id)
    brief = db.get_brief(post["brief_id"]) if post.get("brief_id") else None

    return {
        **post,
        "images": images,
        "brief": brief,
    }


@router.patch("/{post_id}")
async def update_post(post_id: str, updates: PostUpdate):
    """Update a post (body, status, schedule, posted URL)."""
    data = updates.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No updates provided")
    result = db.update_post(post_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    return result


@router.delete("/{post_id}")
async def delete_post(post_id: str):
    """Delete a post and its images."""
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Clean up storage
    images = db.list_images(post_id)
    if images:
        from api.storage import delete_images
        paths = [img["storage_path"] for img in images]
        delete_images(paths)

    db.delete_post(post_id)
    return {"deleted": True}
