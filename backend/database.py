from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/elon_bets")

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String, unique=True, index=True)
    tweet_text = Column(Text)
    tweet_author_id = Column(String)
    tweet_created_at = Column(DateTime)
    event_type = Column(String)
    prediction_id = Column(Integer, ForeignKey("model_predictions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("ModelPrediction", back_populates="event")
    snapshots = relationship("BucketSnapshot", back_populates="event_obj")
    tips = relationship("Tip", back_populates="event_obj")

class BucketSnapshot(Base):
    __tablename__ = "bucket_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    bucket_type = Column(String)
    bucket_name = Column(String)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    event_obj = relationship("Event", back_populates="snapshots")

class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id")) # Redundant but useful for direct lookup
    model_name = Column(String)
    prediction_value = Column(Float)
    prediction_timestamp = Column(DateTime, default=datetime.utcnow)
    is_correct = Column(Boolean, nullable=True) # To be filled after event resolution
    confidence = Column(Float, nullable=True) # Confidence score of the prediction

    event = relationship("Event", back_populates="prediction")

class Tip(Base):
    __tablename__ = "tips"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(String) # Telegram user ID or similar
    tip_value = Column(Float) # The amount of tip
    tip_currency = Column(String) # e.g., "USD", "BTC", "MSK"
    tipped_at = Column(DateTime, default=datetime.utcnow)

    event_obj = relationship("Event", back_populates="tips")


def get_db_engine():
    return create_engine(DATABASE_URL)

def get_db_session():
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

if __name__ == "__main__":
    engine = get_db_engine()
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if they didn't exist).")
