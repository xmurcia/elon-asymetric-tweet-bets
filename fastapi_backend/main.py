import logging

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .metrics import Metrics, MetricsMiddleware
from .models import MarketEvent, MarketOutcome, MarketSyncState, OutcomePriceSnapshot
from .scheduler import init_scheduler
from .webhooks import router as tips_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Elon Asymmetric Tweet Bets API")

# Ensure DB schema exists (cheap, idempotent). Importing tips router also
# runs create_all, but we centralize it here so new tables are created
# even if routes change.
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Lightweight in-memory metrics (for basic monitoring/debugging)
metrics = Metrics()
app.add_middleware(MetricsMiddleware, metrics=metrics)

# BACKEND-JOBS-002: start APScheduler via proper FastAPI lifecycle hooks
init_scheduler(app)

app.include_router(tips_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Elon Asymmetric Tweet Bets API!"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def get_metrics():
    return metrics.snapshot()


@app.get("/events")
def list_events(db: Session = Depends(get_db)):
    events = db.query(MarketEvent).order_by(MarketEvent.updated_at.desc().nullslast(), MarketEvent.id.desc()).all()
    payload = []

    for event in events:
        sorted_outcomes = sorted(event.outcomes, key=lambda o: o.outcome_index)
        outcome_ids = [outcome.id for outcome in sorted_outcomes]

        latest_prices = {}
        latest_timestamp = None
        if outcome_ids:
            subquery = (
                db.query(
                    OutcomePriceSnapshot.outcome_id.label("outcome_id"),
                    func.max(OutcomePriceSnapshot.timestamp).label("latest_ts"),
                )
                .filter(OutcomePriceSnapshot.outcome_id.in_(outcome_ids))
                .group_by(OutcomePriceSnapshot.outcome_id)
                .subquery()
            )

            latest_rows = (
                db.query(OutcomePriceSnapshot)
                .join(
                    subquery,
                    (OutcomePriceSnapshot.outcome_id == subquery.c.outcome_id)
                    & (OutcomePriceSnapshot.timestamp == subquery.c.latest_ts),
                )
                .all()
            )

            for row in latest_rows:
                latest_prices[row.outcome_id] = {
                    "price": row.price,
                    "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                }
                if row.timestamp and (latest_timestamp is None or row.timestamp > latest_timestamp):
                    latest_timestamp = row.timestamp

        outcomes = []
        for outcome in sorted_outcomes:
            latest = latest_prices.get(outcome.id)
            outcomes.append(
                {
                    "id": outcome.id,
                    "outcome_index": outcome.outcome_index,
                    "name": outcome.name,
                    "clob_token_id": outcome.clob_token_id,
                    "latest_price": latest["price"] if latest else None,
                    "latest_price_timestamp": latest["timestamp"] if latest else None,
                }
            )

        payload.append(
            {
                "id": event.id,
                "external_id": event.external_id,
                "source": event.source,
                "slug": event.slug,
                "question": event.question,
                "condition_id": event.condition_id,
                "active": event.active,
                "closed": event.closed,
                "end_date": event.end_date.isoformat() if event.end_date else None,
                "updated_at_external": event.updated_at_external.isoformat() if event.updated_at_external else None,
                "updated_at": event.updated_at.isoformat() if event.updated_at else None,
                "latest_snapshot_at": latest_timestamp.isoformat() if latest_timestamp else None,
                "outcomes": outcomes,
            }
        )

    return payload


@app.get("/events/{event_id}/snapshots")
def event_snapshots(event_id: int, db: Session = Depends(get_db)):
    event = db.query(MarketEvent).filter(MarketEvent.id == event_id).one_or_none()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    snapshots = (
        db.query(OutcomePriceSnapshot, MarketOutcome)
        .join(MarketOutcome, OutcomePriceSnapshot.outcome_id == MarketOutcome.id)
        .filter(MarketOutcome.event_id == event_id)
        .order_by(OutcomePriceSnapshot.timestamp.desc(), MarketOutcome.outcome_index.asc())
        .limit(200)
        .all()
    )

    return {
        "event": {
            "id": event.id,
            "external_id": event.external_id,
            "source": event.source,
            "question": event.question,
        },
        "snapshots": [
            {
                "outcome_id": outcome.id,
                "outcome_index": outcome.outcome_index,
                "outcome_name": outcome.name,
                "price": snapshot.price,
                "timestamp": snapshot.timestamp.isoformat(),
            }
            for snapshot, outcome in snapshots
        ],
    }


@app.get("/events/{event_id}/predictions")
def event_predictions(event_id: int, db: Session = Depends(get_db)):
    event = db.query(MarketEvent).filter(MarketEvent.id == event_id).one_or_none()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    subquery = (
        db.query(
            OutcomePriceSnapshot.outcome_id.label("outcome_id"),
            func.max(OutcomePriceSnapshot.timestamp).label("latest_ts"),
        )
        .join(MarketOutcome, OutcomePriceSnapshot.outcome_id == MarketOutcome.id)
        .filter(MarketOutcome.event_id == event_id)
        .group_by(OutcomePriceSnapshot.outcome_id)
        .subquery()
    )

    rows = (
        db.query(MarketOutcome, OutcomePriceSnapshot)
        .outerjoin(subquery, subquery.c.outcome_id == MarketOutcome.id)
        .outerjoin(
            OutcomePriceSnapshot,
            (OutcomePriceSnapshot.outcome_id == MarketOutcome.id)
            & (OutcomePriceSnapshot.timestamp == subquery.c.latest_ts),
        )
        .filter(MarketOutcome.event_id == event_id)
        .order_by(MarketOutcome.outcome_index.asc())
        .all()
    )

    predictions = []
    for outcome, snapshot in rows:
        predictions.append(
            {
                "outcome_id": outcome.id,
                "outcome_index": outcome.outcome_index,
                "outcome_name": outcome.name,
                "price": snapshot.price if snapshot else None,
                "timestamp": snapshot.timestamp.isoformat() if snapshot and snapshot.timestamp else None,
            }
        )

    return {
        "event": {
            "id": event.id,
            "external_id": event.external_id,
            "source": event.source,
            "question": event.question,
        },
        "predictions": predictions,
    }


@app.get("/coverage")
def coverage(db: Session = Depends(get_db)):
    """Operational verification endpoint.

    Returns best-effort coverage information for real market data sync.
    Always responds even if the external API is down (uses stored DB state).
    """

    total_events = db.query(MarketEvent).count()
    events_with_source_and_external_id = (
        db.query(MarketEvent).filter(MarketEvent.source.isnot(None), MarketEvent.external_id.isnot(None)).count()
    )

    # Expected buckets: sum of distinct outcomes per event (as persisted)
    # Received buckets: same, but also require at least one price snapshot.
    total_outcomes = db.query(MarketOutcome).count()
    from sqlalchemy import func

    outcomes_with_prices = (
        db.query(func.count(func.distinct(MarketOutcome.id)))
        .join(OutcomePriceSnapshot, OutcomePriceSnapshot.outcome_id == MarketOutcome.id)
        .scalar()
        or 0
    )

    latest_price_ts = db.query(OutcomePriceSnapshot.timestamp).order_by(OutcomePriceSnapshot.timestamp.desc()).first()
    latest_price_ts_iso = latest_price_ts[0].isoformat() if latest_price_ts and latest_price_ts[0] else None

    state = db.query(MarketSyncState).filter(MarketSyncState.source == "gamma").one_or_none()

    last_sync = None
    last_sync_ok = None
    last_error = None
    if state:
        last_sync = (state.last_sync_finished_at or state.last_sync_started_at)
        last_sync = last_sync.isoformat() if last_sync else None
        last_sync_ok = bool(state.last_sync_ok)
        last_error = state.last_error

    # Coverage is a heuristic: outcomes_with_prices / total_outcomes
    coverage_pct = 0.0
    if total_outcomes:
        coverage_pct = round(100.0 * (outcomes_with_prices / total_outcomes), 2)

    return {
        "events": {
            "total": total_events,
            "with_valid_source_and_external_id": events_with_source_and_external_id,
        },
        "buckets": {
            "expected": total_outcomes,
            "received_with_prices": outcomes_with_prices,
        },
        "prices": {
            "latest_snapshot_at": latest_price_ts_iso,
        },
        "sync": {
            "source": "gamma",
            "last_sync_at": last_sync,
            "last_sync_ok": last_sync_ok,
            "last_error": last_error,
        },
        "coverage_pct": coverage_pct,
    }
