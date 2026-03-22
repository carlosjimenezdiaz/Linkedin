"""
config.py — Load environment variables and expose typed constants.
All other engine scripts import from here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve repo root (one level up from this file)
REPO_ROOT = Path(__file__).parent.parent
load_dotenv(REPO_ROOT / ".env")

_REQUIRED_KEYS = [
    "APIFY_TOKEN",
    "OPENROUTER_API_KEY",
    "FAL_KEY",
]

def _load(key: str) -> str:
    value = os.environ.get(key, "").strip()
    return value

# Validate all required keys are present
_missing = [k for k in _REQUIRED_KEYS if not _load(k)]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}\n"
        f"Add them to {REPO_ROOT / '.env'}"
    )

# API keys
APIFY_TOKEN: str = _load("APIFY_TOKEN")
OPENROUTER_API_KEY: str = _load("OPENROUTER_API_KEY")
FAL_KEY: str = _load("FAL_KEY")

# Derived paths
DRAFTS_DIR: Path = REPO_ROOT / "content" / "drafts"
PUBLISHED_DIR: Path = REPO_ROOT / "content" / "published"
PROFILE_DIR: Path = REPO_ROOT / "profile"
TEMPLATES_DIR: Path = REPO_ROOT / "templates"
INSPIRATION_DIR: Path = REPO_ROOT / "inspiration"

# Brand constants (used in image prompts and carousel CSS)
BRAND_BG_COLOR = "#0a1628"
BRAND_ACCENT_COLOR = "#c9a84c"
BRAND_NAME = "Carlos Jimenez"

# OpenRouter models
MODEL_WRITER = "anthropic/claude-sonnet-4-5"    # post copy generation
MODEL_SYNTHESIZER = "anthropic/claude-3.5-haiku"  # fast synthesis tasks
MODEL_RESEARCH = "perplexity/sonar"              # web-connected research

# Image generation
NANO_BANANA_MODEL = "fal-ai/nano-banana-2"
