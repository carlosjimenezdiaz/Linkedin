"""
packager.py — Assemble the final draft folder.
Reads content/ideas.md to find the next unprocessed idea for --next-idea mode.
"""
import re
from datetime import datetime
from pathlib import Path

from engine.config import DRAFTS_DIR, REPO_ROOT


def get_next_idea() -> tuple[str, str] | None:
    """
    Read content/ideas.md and return (topic, post_type) for the next idea
    that doesn't already have a draft folder.
    Returns None if all ideas are processed or file is empty.
    """
    ideas_path = REPO_ROOT / "content" / "ideas.md"
    if not ideas_path.exists():
        return None

    ideas_text = ideas_path.read_text()

    # Parse ideas: lines like: - [#001] "Topic title" (type: thought-leadership)
    pattern = re.compile(
        r'\[#(\d+)\]\s+"([^"]+)"\s+\(type:\s+([^)]+)\)'
    )

    existing_slugs = {p.name for p in DRAFTS_DIR.iterdir() if p.is_dir()} if DRAFTS_DIR.exists() else set()

    for match in pattern.finditer(ideas_text):
        idea_num = match.group(1).zfill(3)
        topic = match.group(2)
        post_type = match.group(3).strip()

        # Check if a draft already exists for this idea number
        already_drafted = any(idea_num in slug for slug in existing_slugs)
        if not already_drafted:
            return topic, post_type

    return None


def make_slug(topic: str, idea_num: str = "") -> str:
    """Convert topic to a filesystem-safe slug with date prefix."""
    today = datetime.now().strftime("%Y-%m-%d")
    clean = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    clean = clean[:50]
    prefix = f"{today}-{idea_num}-" if idea_num else f"{today}-"
    return prefix + clean


def print_summary(draft_dir: Path, word_count: int, image_paths: list[Path]) -> None:
    """Print a clean summary of what was generated."""
    print("\n" + "=" * 60)
    print("  DRAFT READY")
    print("=" * 60)
    print(f"  Folder : {draft_dir}")
    print(f"  Post   : {draft_dir / 'post.md'} ({word_count} words)")
    print(f"  Brief  : {draft_dir / 'brief.md'}")
    if image_paths:
        print(f"  Images : {len(image_paths)} file(s)")
        for p in image_paths:
            print(f"    - {p.name}")
    print("=" * 60)
    print("  Next: review post.md, copy to LinkedIn, then save to")
    print(f"  content/published/{draft_dir.name}.md")
    print("=" * 60 + "\n")
