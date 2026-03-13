"""Background jobs for the FastAPI backend.

BACKEND-JOBS-002: Provide a real scheduler integration (not local-only).
Jobs in this file MUST be safe to run repeatedly and should not assume
request context.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import func

from .database import SessionLocal
from .models import Tip

logger = logging.getLogger(__name__)


def job_log_tip_stats() -> None:
    """Periodic job: log basic tip stats.

    Non-destructive. Useful as a smoke job to prove the scheduler is alive
    and DB connectivity works.
    """
    started_at = datetime.now(timezone.utc)
    db = SessionLocal()
    try:
        total_tips_count = db.query(Tip).count()
        total_amount_result = db.query(func.sum(Tip.amount)).scalar()
        total_amount = float(total_amount_result or 0)

        logger.info(
            "[jobs] tip stats | count=%s total_amount_usdc=%.6f | started_at=%s",
            total_tips_count,
            total_amount,
            started_at.isoformat(),
        )
    except Exception:
        logger.exception("[jobs] failed to compute tip stats")
    finally:
        db.close()


def register_jobs(scheduler) -> None:
    """Register APScheduler jobs.

    Idempotent: safe to call multiple times.
    """

    # Hourly stats log (very cheap)
    if not scheduler.get_job("log_tip_stats"):
        scheduler.add_job(
            job_log_tip_stats,
            trigger="interval",
            hours=1,
            id="log_tip_stats",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=60,
        )
