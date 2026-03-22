"""
api/main.py — FastAPI application entry point.

Run with:
  uvicorn api.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import CORS_ORIGINS
from api.routes import pipeline, ideas, posts, migrate, influencers

app = FastAPI(
    title="LinkedIn Content Engine API",
    description="Web API for the LinkedIn content generation pipeline.",
    version="1.0.0",
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(pipeline.router)
app.include_router(ideas.router)
app.include_router(posts.router)
app.include_router(migrate.router)
app.include_router(influencers.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
