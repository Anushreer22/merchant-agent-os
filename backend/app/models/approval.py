from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from app.database import Base


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    approval_id = Column(String, unique=True, index=True, nullable=False)
    negotiation_id = Column(String, index=True, nullable=False)
    buyer_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    requested_discount = Column(Numeric(5, 4), nullable=False)
    proposed_discount = Column(Numeric(5, 4), nullable=False)
    final_price = Column(Numeric(12, 2), nullable=False)
    margin_after_discount = Column(Numeric(5, 4), nullable=True)
    policy_version = Column(String, nullable=False)
    reason_code = Column(String, nullable=False)
    status = Column(String, default="PENDING", nullable=False)
    human_user_id = Column(String, nullable=True)
    approval_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)
