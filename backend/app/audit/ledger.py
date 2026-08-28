from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.audit import AuditEvent
from app.audit.hashing import compute_event_hash, canonicalize_payload, compute_sha256


def append_audit_event(
    db: Session,
    actor: str,
    action_type: str,
    payload: dict,
    policy_version: str = None,
    negotiation_id: str = None,
    razorpay_entity_id: str = None,
) -> AuditEvent:
    last = db.query(AuditEvent).order_by(AuditEvent.id.desc()).first()
    previous_hash = "GENESIS" if last is None else last.hash

    payload_hash, event_hash = compute_event_hash(previous_hash, payload)

    event = AuditEvent(
        event_id=f"EVT-{uuid4().hex[:12]}",
        actor=actor,
        action_type=action_type,
        policy_version=policy_version,
        negotiation_id=negotiation_id,
        razorpay_entity_id=razorpay_entity_id,
        payload=payload,
        payload_hash=payload_hash,
        previous_hash=previous_hash,
        hash=event_hash,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def validate_audit_chain(db: Session) -> dict:
    events = db.query(AuditEvent).order_by(AuditEvent.id).all()
    if not events:
        return {"valid": True, "events_checked": 0, "first_invalid_event_id": None}

    for i, event in enumerate(events):
        expected_previous = "GENESIS" if i == 0 else events[i - 1].hash

        if event.previous_hash != expected_previous:
            return {"valid": False, "events_checked": i + 1, "first_invalid_event_id": event.event_id}

        expected_payload_hash = compute_sha256(canonicalize_payload(event.payload))
        if event.payload_hash != expected_payload_hash:
            return {"valid": False, "events_checked": i + 1, "first_invalid_event_id": event.event_id}

        expected_hash = compute_sha256(event.previous_hash + event.payload_hash)
        if event.hash != expected_hash:
            return {"valid": False, "events_checked": i + 1, "first_invalid_event_id": event.event_id}

    return {"valid": True, "events_checked": len(events), "first_invalid_event_id": None}
