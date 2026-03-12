from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
from .database import Base

class Tip(Base):
    __tablename__ = "tips"

    id = Column(Integer, primary_key=True, index=True)
    sender_address = Column(String, index=True)
    amount = Column(Numeric(20, 6))
    timestamp = Column(DateTime)
    transaction_hash = Column(String, unique=True, index=True)
    is_confirmed = Column(Boolean, default=False)

