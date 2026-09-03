import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.approval import Approval
from app.models.negotiation import Negotiation
from app.audit.ledger import append_audit_event
from app.services.notification_service import notify


def create_approval(db: Session, negotiation_id: str) -> Approval:
    negotiation = db.query(Negotiation).filter(
        Negotiation.negotiation_id == negotiation_id
    ).first()
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    if negotiation.decision != "APPROVAL_REQUIRED":
        raise HTTPException(status_code=400, detail="No approval needed for this negotiation")

    approval = Approval(
        approval_id=f"APR-{uuid.uuid4()}",
        negotiation_id=negotiation.negotiation_id,
        buyer_id=negotiation.buyer_id,
        product_id=negotiation.product_id,
        quantity=negotiation.quantity,
        requested_discount=negotiation.requested_discount,
        proposed_discount=negotiation.final_discount,
        final_price=negotiation.final_amount,
        policy_version=negotiation.policy_version,
        reason_code=negotiation.reason_code,
        status="PENDING",
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


def decide_approval(
    db: Session,
    approval_id: str,
    decision: str,
    human_user_id: str,
    reason: str = None,
) -> Approval:
    approval = db.query(Approval).filter(Approval.approval_id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != "PENDING":
        raise HTTPException(status_code=409, detail="Approval already decided")

    approval.status = decision
    approval.human_user_id = human_user_id
    approval.approval_reason = reason
    approval.decided_at = datetime.now(timezone.utc)

    negotiation = db.query(Negotiation).filter(
        Negotiation.negotiation_id == approval.negotiation_id
    ).first()
    if negotiation:
        if decision == "APPROVED":
            negotiation.status = "APPROVED"
            negotiation.final_discount = approval.proposed_discount
            negotiation.final_amount = approval.final_price
        else:
            negotiation.status = "REJECTED"

    db.commit()
    db.refresh(approval)

    action_type = "APPROVAL_GRANTED" if decision == "APPROVED" else "APPROVAL_REJECTED"
    try:
        append_audit_event(
            db,
            actor="HUMAN",
            action_type=action_type,
            payload={
                "approval_id": approval_id,
                "negotiation_id": approval.negotiation_id,
                "decision": decision,
                "human_user_id": human_user_id,
            },
            policy_version=approval.policy_version,
            negotiation_id=approval.negotiation_id,
        )
    except Exception:
        pass

    return approval


def get_approval(db: Session, approval_id: str) -> Approval:
    approval = db.query(Approval).filter(Approval.approval_id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval
