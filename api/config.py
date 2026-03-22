"""
api/config.py — Supabase client initialization and API config.
Extends engine/config.py with Supabase credentials.
"""
import os
from supabase import create_client, Client
from engine.config import REPO_ROOT
from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise EnvironmentError(
        "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env\n"
        "Add them to configure Supabase."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Storage bucket name for generated images
IMAGE_BUCKET = "post-images"

# CORS origins for local development
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
