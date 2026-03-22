"""
api/routes/influencers.py — Influencer list CRUD endpoints.

Reads and writes directly to profile/influencers.json.
"""
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/influencers", tags=["influencers"])

INFLUENCERS_PATH = Path(__file__).resolve().parents[2] / "profile" / "influencers.json"


class InfluencerCreate(BaseModel):
    name: str
    url: str
    pillar: str
    note: Optional[str] = None


def _read_file() -> dict:
    """Read the influencers JSON file."""
    with open(INFLUENCERS_PATH, "r") as f:
        return json.load(f)


def _write_file(data: dict) -> None:
    """Write the influencers JSON file."""
    with open(INFLUENCERS_PATH, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


@router.get("")
async def list_influencers():
    """Return the list of tracked influencers."""
    data = _read_file()
    return data["influencers"]


@router.post("", status_code=201)
async def add_influencer(influencer: InfluencerCreate):
    """Add a new influencer to the tracking list."""
    data = _read_file()

    # Check for duplicate by name (case-insensitive)
    for existing in data["influencers"]:
        if existing["name"].lower() == influencer.name.lower():
            raise HTTPException(
                status_code=409,
                detail=f"Influencer '{influencer.name}' already exists",
            )

    entry = {"name": influencer.name, "url": influencer.url, "pillar": influencer.pillar}
    if influencer.note:
        entry["note"] = influencer.note

    data["influencers"].append(entry)
    _write_file(data)
    return entry


@router.delete("/{name}")
async def remove_influencer(name: str):
    """Remove an influencer by name (case-insensitive match)."""
    data = _read_file()
    original_len = len(data["influencers"])
    data["influencers"] = [
        inf for inf in data["influencers"] if inf["name"].lower() != name.lower()
    ]

    if len(data["influencers"]) == original_len:
        raise HTTPException(status_code=404, detail=f"Influencer '{name}' not found")

    _write_file(data)
    return {"detail": f"Influencer '{name}' removed"}
