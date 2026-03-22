"""
api/routes/migrate.py — One-time migration endpoints.
Parse existing ideas.md and draft folders into Supabase.
"""
import re
from pathlib import Path
from fastapi import APIRouter

from engine.config import REPO_ROOT, DRAFTS_DIR
from api import db
from api.storage import upload_image

router = APIRouter(prefix="/api/migrate", tags=["migrate"])


@router.post("/ideas")
async def migrate_ideas():
    """Parse content/ideas.md into the ideas table."""
    ideas_path = REPO_ROOT / "content" / "ideas.md"
    if not ideas_path.exists():
        return {"error": "ideas.md not found"}

    text = ideas_path.read_text()
    pattern = re.compile(r'\[#(\d+)\]\s+"([^"]+)"\s+\(type:\s+([^)]+)\)')

    # Try to extract theme from section headers
    current_theme = None
    created = []

    for line in text.splitlines():
        theme_match = re.match(r"##\s+\d{4}-\d{2}-\d{2}\s+Theme:\s+(.+)", line)
        if theme_match:
            current_theme = theme_match.group(1).strip()
            continue

        pillar_match = re.match(r"###\s+(.+)", line)
        if pillar_match:
            current_theme = pillar_match.group(1).strip()
            continue

        idea_match = pattern.search(line)
        if idea_match:
            number = int(idea_match.group(1))
            title = idea_match.group(2)
            post_type = idea_match.group(3).strip()

            # Normalize post type
            type_map = {
                "thought-leadership": "thought-leadership",
                "story": "story",
                "news-commentary": "news",
                "news": "news",
                "cta": "cta",
            }
            post_type = type_map.get(post_type, "thought-leadership")

            # Check if already exists
            existing = db.list_ideas()
            if any(i["number"] == number for i in existing):
                continue

            row = {
                "number": number,
                "title": title,
                "post_type": post_type,
                "theme": current_theme,
                "status": "backlog",
            }
            result = db.supabase.table("ideas").insert(row).execute()
            created.append(result.data[0])

    return {"migrated": len(created), "ideas": created}


@router.post("/drafts")
async def migrate_drafts():
    """Parse existing draft folders into posts + briefs tables."""
    if not DRAFTS_DIR.exists():
        return {"error": "drafts directory not found"}

    migrated = []

    for draft_dir in sorted(DRAFTS_DIR.iterdir()):
        if not draft_dir.is_dir():
            continue

        post_path = draft_dir / "post.md"
        brief_path = draft_dir / "brief.md"

        if not post_path.exists():
            continue

        post_text = post_path.read_text()

        # Parse YAML frontmatter
        meta = {}
        body = post_text
        if post_text.startswith("---"):
            parts = post_text.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].strip().splitlines():
                    if ":" in line:
                        key, val = line.split(":", 1)
                        meta[key.strip()] = val.strip().strip('"').strip("'")
                body = parts[2].strip()

        slug = meta.get("slug", draft_dir.name)

        # Check if already migrated
        existing = db.list_posts()
        if any(p["slug"] == slug for p in existing):
            continue

        # Migrate brief if exists
        brief_id = None
        if brief_path.exists():
            brief_text = brief_path.read_text()
            topic_match = re.search(r'topic:\s*"([^"]+)"', brief_text)
            topic = topic_match.group(1) if topic_match else slug

            brief_row = db.create_brief(
                topic=topic,
                full_brief_md=brief_text,
            )
            brief_id = brief_row["id"]

        # Migrate post
        topic = meta.get("topic", slug.replace("-", " "))
        post_row = db.create_post(
            slug=slug,
            topic=topic,
            post_type=meta.get("type", "thought-leadership"),
            pillar=meta.get("pillar", "general"),
            body=body,
            word_count=int(meta.get("word_count", len(body.split()))),
            image_type=meta.get("image_type"),
            brief_id=brief_id,
        )

        # Migrate images
        images_dir = draft_dir / "images"
        if images_dir.exists():
            for img_path in sorted(images_dir.rglob("*.png")):
                storage_path = f"{slug}/{img_path.name}"
                public_url = upload_image(img_path, storage_path)

                slide_num = None
                slide_match = re.search(r"slide-(\d+)", img_path.stem)
                if slide_match:
                    slide_num = int(slide_match.group(1))

                img_type = "carousel" if slide_num else img_path.stem
                db.create_image(
                    post_id=post_row["id"],
                    image_type=img_type,
                    storage_path=storage_path,
                    public_url=public_url,
                    slide_number=slide_num,
                )

        migrated.append({"slug": slug, "post_id": post_row["id"]})

    return {"migrated": len(migrated), "posts": migrated}
