"""
api/progress.py — In-memory progress store for SSE streaming.
Single-user app: a simple dict suffices.
"""
import asyncio
import json
from dataclasses import dataclass, field
from typing import AsyncGenerator

# Global progress store: run_id -> list of events
_progress: dict[str, list[dict]] = {}
_events: dict[str, asyncio.Event] = {}


def init_run(run_id: str) -> None:
    """Initialize progress tracking for a pipeline run."""
    _progress[run_id] = []
    _events[run_id] = asyncio.Event()


def push_event(run_id: str, event_type: str, data: dict) -> None:
    """Push a progress event for a pipeline run."""
    if run_id not in _progress:
        return
    _progress[run_id].append({"event": event_type, "data": data})
    if run_id in _events:
        _events[run_id].set()


def push_progress(run_id: str, phase: str, message: str, pct: int) -> None:
    """Convenience: push a progress event."""
    push_event(run_id, "progress", {"phase": phase, "message": message, "pct": pct})


def push_complete(run_id: str, post_id: str = None, brief_id: str = None) -> None:
    """Convenience: push a completion event."""
    push_event(run_id, "complete", {"post_id": post_id, "brief_id": brief_id})


def push_error(run_id: str, message: str, phase: str = None) -> None:
    """Convenience: push an error event."""
    push_event(run_id, "error", {"message": message, "phase": phase})


async def stream_events(run_id: str) -> AsyncGenerator[str, None]:
    """Yield SSE-formatted events as they arrive."""
    if run_id not in _progress:
        yield f"event: error\ndata: {json.dumps({'message': 'Run not found'})}\n\n"
        return

    sent = 0
    while True:
        # Wait for new events
        if run_id in _events:
            _events[run_id].clear()

        # Send any unsent events
        events = _progress.get(run_id, [])
        while sent < len(events):
            evt = events[sent]
            yield f"event: {evt['event']}\ndata: {json.dumps(evt['data'])}\n\n"
            sent += 1

            # Stop after complete or error
            if evt["event"] in ("complete", "error"):
                # Cleanup after a short delay
                _cleanup(run_id)
                return

        # Wait for next event (with timeout to keep connection alive)
        if run_id in _events:
            try:
                await asyncio.wait_for(_events[run_id].wait(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send keepalive
                yield ": keepalive\n\n"


def _cleanup(run_id: str) -> None:
    """Remove completed run from memory."""
    _progress.pop(run_id, None)
    _events.pop(run_id, None)
