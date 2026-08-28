from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, func
from app.database import Base


class Negotiation(Base):
    __tablename__ = "negotiations"

    id = Column(Integer, primary_key=True, index=True)
    negotiation_id = Column(String, unique=True, index=True, nullable=False)
    buyer_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    requested_discount = Column(Numeric(5, 4), nullable=False)
    final_discount = Column(Numeric(5, 4), nullable=False)
    final_amount = Column(Numeric(12, 2), nullable=False)
    decision = Column(String, nullable=False)
    requires_human_approval = Column(Boolean, nullable=False)
    policy_version = Column(String, nullable=False)
    reason_code = Column(String, nullable=False)
    status = Column(String, default="PENDING", nullable=False)
    idempotency_key = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
