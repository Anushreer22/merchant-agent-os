from sqlalchemy import Column, Integer, String, Numeric, JSON, DateTime, func
from app.database import Base


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    budget = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    max_single_transaction = Column(Numeric(14, 2), nullable=False)
    preferred_categories = Column(JSON, default=list)
    negotiation_strategy = Column(String, default="balanced", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
