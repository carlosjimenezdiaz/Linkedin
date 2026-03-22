"""
api/routes/pipeline.py — Pipeline endpoints + SSE progress streaming.
"""
import asyncio
import traceback
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse

from api.models import PipelineRequest, PipelineRunOut, WriteRequest, ImageRequest
from api import db
from api.progress import (
    init_run,
    push_progress,
    push_complete,
    push_error,
    stream_events,
)

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


def _run_full_pipeline_task(run_id: str, topic: str, post_type: str, image_type: str, idea_id: str = None):
    """Background task: run the full pipeline with progress updates."""
    from engine.supabase_adapter import run_full_pipeline

    def on_progress(phase, message, pct):
        push_progress(run_id, phase, message, pct)
        db.update_pipeline_run(run_id, {
            "current_phase": phase,
            "progress_pct": pct,
        })

    try:
        result = run_full_pipeline(
            topic=topic,
            post_type=post_type,
            image_type=image_type,
            idea_id=idea_id,
            on_progress=on_progress,
        )
        db.update_pipeline_run(run_id, {
            "status": "completed",
            "post_id": result["post_id"],
            "progress_pct": 100,
            "completed_at": "now()",
        })
        push_complete(run_id, post_id=result["post_id"], brief_id=result["brief_id"])

    except Exception as e:
        db.update_pipeline_run(run_id, {
            "status": "failed",
            "error_message": str(e),
        })
        push_error(run_id, str(e))
        traceback.print_exc()


def _run_research_task(run_id: str, topic: str, idea_id: str = None):
    """Background task: research only."""
    from engine.supabase_adapter import run_research_only

    def on_progress(phase, message, pct):
        push_progress(run_id, phase, message, pct)
        db.update_pipeline_run(run_id, {
            "current_phase": phase,
            "progress_pct": pct,
        })

    try:
        result = run_research_only(topic=topic, idea_id=idea_id, on_progress=on_progress)
        db.update_pipeline_run(run_id, {
            "status": "completed",
            "progress_pct": 100,
            "completed_at": "now()",
        })
        push_complete(run_id, brief_id=result["brief_id"])

    except Exception as e:
        db.update_pipeline_run(run_id, {
            "status": "failed",
            "error_message": str(e),
        })
        push_error(run_id, str(e))
        traceback.print_exc()


@router.post("/full")
async def start_full_pipeline(req: PipelineRequest, background_tasks: BackgroundTasks):
    """Start the full pipeline (research → write → image). Returns run_id for SSE streaming."""
    run = db.create_pipeline_run(run_type="full", idea_id=req.idea_id)
    run_id = run["id"]
    init_run(run_id)

    background_tasks.add_task(
        _run_full_pipeline_task,
        run_id=run_id,
        topic=req.topic,
        post_type=req.post_type,
        image_type=req.image_type,
        idea_id=req.idea_id,
    )

    return {"run_id": run_id}


@router.post("/research")
async def start_research(req: PipelineRequest, background_tasks: BackgroundTasks):
    """Start research only. Returns run_id for SSE streaming."""
    run = db.create_pipeline_run(run_type="research-only", idea_id=req.idea_id)
    run_id = run["id"]
    init_run(run_id)

    background_tasks.add_task(
        _run_research_task,
        run_id=run_id,
        topic=req.topic,
        idea_id=req.idea_id,
    )

    return {"run_id": run_id}


@router.get("/{run_id}/stream")
async def stream_pipeline_progress(run_id: str):
    """SSE endpoint — stream real-time progress events for a pipeline run."""
    return StreamingResponse(
        stream_events(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{run_id}")
async def get_pipeline_run(run_id: str):
    """Get current status of a pipeline run."""
    run = db.get_pipeline_run(run_id)
    if not run:
        return {"error": "Run not found"}, 404
    return run
