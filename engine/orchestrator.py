"""
orchestrator.py — CLI entry point for the LinkedIn content engine.

Usage examples:
  python -m engine.orchestrator --topic "data leakage in financial ML" --type thought-leadership --image branded
  python -m engine.orchestrator --topic "agentic AI" --type story --image carousel
  python -m engine.orchestrator --research-only --topic "LLM agents in finance"
  python -m engine.orchestrator --draft content/drafts/2026-03-17-data-leakage/brief.md --image infographic
  python -m engine.orchestrator --next-idea --image auto
"""
import argparse
import re
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LinkedIn Content Engine — research, write, and generate images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--topic", type=str, help="Research topic / post subject")
    parser.add_argument(
        "--type",
        type=str,
        default="thought-leadership",
        choices=["thought-leadership", "story", "news", "cta"],
        help="Post type (default: thought-leadership)",
    )
    parser.add_argument(
        "--image",
        type=str,
        default="auto",
        choices=["diagram", "branded", "infographic", "carousel", "auto", "none"],
        help="Image type (default: auto — inferred from post structure)",
    )
    parser.add_argument(
        "--research-only",
        action="store_true",
        help="Only run research, skip writing and image generation",
    )
    parser.add_argument(
        "--draft",
        type=str,
        help="Path to an existing brief.md — skip research phase",
    )
    parser.add_argument(
        "--next-idea",
        action="store_true",
        help="Pick the next unprocessed idea from content/ideas.md",
    )
    return parser.parse_args()


def _infer_image_type_from_post(post_type: str, post_path: Path) -> str:
    """Auto-detect best image type from post content."""
    text = post_path.read_text()
    numbered = re.findall(r"^\d+\.", text, re.MULTILINE)
    if len(numbered) >= 3:
        return "carousel"
    if re.search(r"\d+%|\$\d+|\d+x\b", text):
        return "infographic"
    return "diagram"


def main() -> None:
    args = _parse_args()

    # Lazy imports — config validates env vars on import, so errors surface early
    try:
        from engine.config import DRAFTS_DIR, REPO_ROOT
    except EnvironmentError as e:
        print(f"\nConfiguration error:\n{e}\n")
        sys.exit(1)

    from engine.packager import get_next_idea, make_slug, print_summary

    # ---- Resolve topic + post type ----
    post_type = args.type
    brief_path = None

    if args.next_idea:
        result = get_next_idea()
        if result is None:
            print("No unprocessed ideas found in content/ideas.md.")
            sys.exit(0)
        topic, post_type = result
        print(f"\n[orchestrator] Next idea: '{topic}' (type: {post_type})")

    elif args.draft:
        brief_path = Path(args.draft)
        if not brief_path.exists():
            print(f"Brief file not found: {brief_path}")
            sys.exit(1)
        # Extract topic from brief frontmatter
        brief_text = brief_path.read_text()
        topic_match = re.search(r'topic:\s*"([^"]+)"', brief_text)
        topic = topic_match.group(1) if topic_match else brief_path.parent.name
        print(f"\n[orchestrator] Using existing brief: {brief_path}")

    elif args.topic:
        topic = args.topic

    else:
        print("Error: provide --topic, --draft, or --next-idea")
        sys.exit(1)

    # ---- Build slug and draft directory ----
    # Try to find idea number for slug
    idea_num = ""
    if args.next_idea:
        from engine.config import REPO_ROOT
        ideas_path = REPO_ROOT / "content" / "ideas.md"
        if ideas_path.exists():
            match = re.search(r'\[#(\d+)\].*?' + re.escape(topic[:30]), ideas_path.read_text())
            if match:
                idea_num = match.group(1).zfill(3)

    slug = make_slug(topic, idea_num)
    draft_dir = DRAFTS_DIR / slug
    draft_dir.mkdir(parents=True, exist_ok=True)

    print(f"[orchestrator] Draft folder: {draft_dir}")

    # ---- Phase 1: Research ----
    if brief_path is None:
        print("\n[Phase 1/3] Research")
        from engine.research import build_brief
        brief_path = build_brief(topic, draft_dir)
    else:
        # Copy existing brief into draft dir if it's not already there
        target = draft_dir / "brief.md"
        if brief_path != target:
            target.write_text(brief_path.read_text())
            brief_path = target

    if args.research_only:
        print(f"\n[orchestrator] Research complete. Brief at: {brief_path}")
        return

    # ---- Phase 2: Write ----
    print("\n[Phase 2/3] Writing post")
    from engine.generate import generate_post
    post_path, inferred_image_type = generate_post(brief_path, post_type, slug)

    # Read word count from frontmatter
    post_text = post_path.read_text()
    wc_match = re.search(r"word_count:\s*(\d+)", post_text)
    word_count = int(wc_match.group(1)) if wc_match else len(post_text.split())

    # Read pillar from frontmatter
    pillar_match = re.search(r"pillar:\s*(\S+)", post_text)
    pillar = pillar_match.group(1) if pillar_match else "general"

    # ---- Phase 3: Images ----
    image_type = args.image
    if image_type == "auto":
        image_type = inferred_image_type
    print(f"\n[Phase 3/3] Generating image ({image_type})")

    images_dir = draft_dir / "images"
    image_paths: list[Path] = []

    if image_type == "none":
        print("  [images] Skipping image generation.")
    elif image_type == "carousel":
        from engine.carousel import render_carousel
        carousel_dir = images_dir / "carousel"
        image_paths = render_carousel(post_path, carousel_dir, pillar)
    else:
        from engine.images import generate_image
        image_paths = generate_image(post_path, image_type, images_dir, pillar)

    # ---- Done ----
    print_summary(draft_dir, word_count, image_paths)


if __name__ == "__main__":
    main()
