"""APScheduler integration for the FastAPI app.

BACKEND-JOBS-002: scheduler must start in real deployments (uvicorn/gunicorn)
via FastAPI lifespan hooks, not by importing modules.

Notes:
- Uses BackgroundScheduler (thread-based). Works with standard uvicorn.
- In multi-worker deployments, each worker would start its own scheduler.
  If that becomes a problem, move to an external scheduler (Celery/Redis)
  or a single dedicated worker.
"""

from __future__ import annotations

import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler

from .jobs import register_jobs

logger = logging.getLogger(__name__)

_SCHEDULER: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _SCHEDULER
    if _SCHEDULER is None:
        _SCHEDULER = BackgroundScheduler(timezone="UTC")
    return _SCHEDULER


def init_scheduler(app) -> None:
    """Attach startup/shutdown handlers to the FastAPI app."""

    @app.on_event("startup")
    def _start_scheduler() -> None:
        # Allow disabling scheduler for tests or specific deployments.
        if os.getenv("SCHEDULER_ENABLED", "true").lower() in {"0", "false", "no"}:
            logger.info("[scheduler] disabled via SCHEDULER_ENABLED")
            return

        scheduler = get_scheduler()
        try:
            register_jobs(scheduler)
            if not scheduler.running:
                scheduler.start()
            logger.info("[scheduler] started | jobs=%s", len(scheduler.get_jobs()))
        except Exception:
            logger.exception("[scheduler] failed to start")

    @app.on_event("shutdown")
    def _stop_scheduler() -> None:
        scheduler = get_scheduler()
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("[scheduler] stopped")
