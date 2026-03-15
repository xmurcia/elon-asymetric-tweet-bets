"""SQLAlchemy models for the FastAPI backend.

This backend originally only stored tips. For the MVP we also persist
real Polymarket market data (Gamma/CLOB depending on configuration).

We keep the schema minimal and append-only for prices.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class Tip(Base):
    __tablename__ = "tips"

    id = Column(Integer, primary_key=True, index=True)
    sender_address = Column(String, index=True)
    amount = Column(Numeric(20, 6))
    timestamp = Column(DateTime)
    transaction_hash = Column(String, unique=True, index=True)
    is_confirmed = Column(Boolean, default=False)


class MarketEvent(Base):
    """Polymarket market as an 'event' in our app."""

    __tablename__ = "market_events"

    id = Column(Integer, primary_key=True)

    # Gamma market id (stringified int), e.g. "531202"
    external_id = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, default="gamma", index=True, nullable=False)

    slug = Column(String, index=True, nullable=True)
    question = Column(Text, nullable=False)
    condition_id = Column(String, index=True, nullable=True)

    active = Column(Boolean, default=True)
    closed = Column(Boolean, default=False)

    end_date = Column(DateTime, nullable=True)
    updated_at_external = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    outcomes = relationship("MarketOutcome", back_populates="event", cascade="all, delete-orphan")


class MarketOutcome(Base):
    __tablename__ = "market_outcomes"
    __table_args__ = (
        UniqueConstraint("event_id", "outcome_index", name="uq_event_outcome_index"),
    )

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("market_events.id", ondelete="CASCADE"), index=True, nullable=False)

    # Index in Gamma 'outcomes' list (0..n-1). Stable for binary markets.
    outcome_index = Column(Integer, nullable=False)

    name = Column(String, nullable=False)

    # Optional: some markets expose clobTokenIds[] corresponding to outcomes
    clob_token_id = Column(String, index=True, nullable=True)

    event = relationship("MarketEvent", back_populates="outcomes")
    price_snapshots = relationship(
        "OutcomePriceSnapshot", back_populates="outcome", cascade="all, delete-orphan"
    )


class OutcomePriceSnapshot(Base):
    __tablename__ = "outcome_price_snapshots"

    id = Column(Integer, primary_key=True)
    outcome_id = Column(Integer, ForeignKey("market_outcomes.id", ondelete="CASCADE"), index=True, nullable=False)

    # For now we persist best-effort "probability" price from Gamma outcomePrices[]
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)

    outcome = relationship("MarketOutcome", back_populates="price_snapshots")


class MarketSyncState(Base):
    """Singleton-ish table to track last successful sync and basic stats."""

    __tablename__ = "market_sync_state"

    id = Column(Integer, primary_key=True)

    source = Column(String, unique=True, index=True, nullable=False)

    last_sync_started_at = Column(DateTime, nullable=True)
    last_sync_finished_at = Column(DateTime, nullable=True)
    last_sync_ok = Column(Boolean, default=False)
    last_error = Column(Text, nullable=True)

