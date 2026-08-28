from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit import AuditEvent
from app.audit.ledger import validate_audit_chain

router = APIRouter()


@router.get("/")
def list_audit_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    events = db.query(AuditEvent).order_by(AuditEvent.id).offset(skip).limit(limit).all()
    return [
        {
            "event_id": e.event_id,
            "timestamp": e.timestamp,
            "actor": e.actor,
            "action_type": e.action_type,
            "policy_version": e.policy_version,
            "negotiation_id": e.negotiation_id,
            "razorpay_entity_id": e.razorpay_entity_id,
            "payload_hash": e.payload_hash,
            "previous_hash": e.previous_hash,
            "hash": e.hash,
            "created_at": e.created_at,
        }
        for e in events
    ]


@router.get("/verify")
def verify_audit_chain(db: Session = Depends(get_db)):
    return validate_audit_chain(db)
