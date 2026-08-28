from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    actor = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    policy_version = Column(String, nullable=True)
    negotiation_id = Column(String, nullable=True)
    razorpay_entity_id = Column(String, nullable=True)
    payload = Column(JSON, nullable=False)
    payload_hash = Column(String, nullable=False)
    previous_hash = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
