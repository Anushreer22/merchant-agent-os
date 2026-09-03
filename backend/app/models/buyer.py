from sqlalchemy import Column, Integer, String, Numeric, Float, JSON, DateTime, func
from app.database import Base


class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    budget = Column(Numeric(14, 2))
    currency = Column(String(3), default="INR")
    max_single_transaction = Column(Numeric(14, 2))
    preferred_categories = Column(JSON, default=list)
    negotiation_strategy = Column(String, default="balanced")
    # new fields
    trust_score = Column(Float, default=0.0)
    total_transactions = Column(Integer, default=0)
    successful_transactions = Column(Integer, default=0)
    on_time_payments = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
