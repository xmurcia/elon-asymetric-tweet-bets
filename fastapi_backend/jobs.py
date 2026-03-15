"""Background jobs for the FastAPI backend.

BACKEND-JOBS-002: Provide a real scheduler integration (not local-only).
Jobs in this file MUST be safe to run repeatedly and should not assume
request context.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from sqlalchemy import func

from .database import SessionLocal
from .market_data import fetch_gamma_markets, now_utc, pair_outcomes_with_prices
from .models import (
    MarketEvent,
    MarketOutcome,
    MarketSyncState,
    OutcomePriceSnapshot,
    Tip,
)

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


def job_sync_markets_gamma() -> None:
    """Periodic job: sync markets/outcomes/prices from Gamma into Postgres.

    Fail-soft by design: if Gamma is down, we record the error in
    MarketSyncState and exit without raising.
    """

    started_at = now_utc()
    db = SessionLocal()

    # Upsert state row
    state = db.query(MarketSyncState).filter(MarketSyncState.source == "gamma").one_or_none()
    if state is None:
        state = MarketSyncState(source="gamma")
        db.add(state)
        db.commit()
        db.refresh(state)

    state.last_sync_started_at = started_at
    state.last_sync_ok = False
    state.last_error = None
    db.commit()

    try:
        markets = fetch_gamma_markets()
        logger.info("[jobs] gamma sync | markets=%s | started_at=%s", len(markets), started_at.isoformat())

        for m in markets:
            event = db.query(MarketEvent).filter(MarketEvent.external_id == m.external_id).one_or_none()
            if event is None:
                event = MarketEvent(external_id=m.external_id, source="gamma", question=m.question)
                db.add(event)
                db.flush()  # get id

            # update
            event.slug = m.slug
            event.question = m.question
            event.condition_id = m.condition_id
            event.active = m.active
            event.closed = m.closed
            event.end_date = m.end_date
            event.updated_at_external = m.updated_at_external
            event.updated_at = now_utc()

            # outcomes + prices
            pairs = pair_outcomes_with_prices(m.outcomes, m.outcome_prices)
            for idx, name, price in pairs:
                outcome = (
                    db.query(MarketOutcome)
                    .filter(MarketOutcome.event_id == event.id, MarketOutcome.outcome_index == idx)
                    .one_or_none()
                )
                if outcome is None:
                    outcome = MarketOutcome(event_id=event.id, outcome_index=idx, name=name)
                    db.add(outcome)
                    db.flush()
                else:
                    outcome.name = name

                # map optional token id
                if m.clob_token_ids and idx < len(m.clob_token_ids):
                    outcome.clob_token_id = m.clob_token_ids[idx]

                if price is not None:
                    db.add(
                        OutcomePriceSnapshot(
                            outcome_id=outcome.id,
                            price=float(price),
                            timestamp=now_utc(),
                        )
                    )

        state.last_sync_ok = True
        state.last_sync_finished_at = now_utc()
        db.commit()

    except Exception as e:
        logger.exception("[jobs] gamma sync failed")
        state.last_sync_ok = False
        state.last_sync_finished_at = now_utc()
        state.last_error = str(e)
        db.commit()
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

    # Market sync (default every 5 minutes)
    interval_s = int(os.getenv("MARKET_SYNC_INTERVAL_SECONDS") or "300")
    if not scheduler.get_job("sync_markets_gamma"):
        scheduler.add_job(
            job_sync_markets_gamma,
            trigger="interval",
            seconds=interval_s,
            id="sync_markets_gamma",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=60,
        )
