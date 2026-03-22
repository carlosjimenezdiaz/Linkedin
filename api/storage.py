"""
api/storage.py — Supabase Storage helpers for image upload/download.
"""
from pathlib import Path
from api.config import supabase, IMAGE_BUCKET, SUPABASE_URL


def upload_image(local_path: Path, storage_path: str) -> str:
    """
    Upload an image to Supabase Storage.
    Returns the public URL.
    """
    with open(local_path, "rb") as f:
        data = f.read()

    supabase.storage.from_(IMAGE_BUCKET).upload(
        storage_path,
        data,
        file_options={"content-type": "image/png", "upsert": "true"},
    )

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{IMAGE_BUCKET}/{storage_path}"
    return public_url


def delete_images(storage_paths: list[str]) -> None:
    """Delete images from Supabase Storage."""
    if storage_paths:
        supabase.storage.from_(IMAGE_BUCKET).remove(storage_paths)
