from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.negotiation import NegotiationRequest, NegotiationResponse
from app.services.negotiation_service import create_negotiation
from app.models.negotiation import Negotiation
from typing import List, Optional

router = APIRouter()


@router.post("/", response_model=NegotiationResponse)
def negotiate(request: NegotiationRequest, db: Session = Depends(get_db)):
    return create_negotiation(
        db=db,
        buyer_id=request.buyer_id,
        product_id=request.product_id,
        quantity=request.quantity,
        requested_discount=request.requested_discount,
        idempotency_key=request.idempotency_key,
    )


@router.get("/")
def list_negotiations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    rows = db.query(Negotiation).order_by(Negotiation.id.desc()).offset(skip).limit(limit).all()
    return [
        {
            "negotiation_id": r.negotiation_id,
            "buyer_id": r.buyer_id,
            "product_id": r.product_id,
            "quantity": r.quantity,
            "requested_discount": float(r.requested_discount),
            "final_discount": float(r.final_discount),
            "final_amount": float(r.final_amount),
            "decision": r.decision,
            "status": r.status,
            "policy_version": r.policy_version,
            "reason_code": r.reason_code,
            "requires_human_approval": r.requires_human_approval,
            "created_at": r.created_at,
        }
        for r in rows
    ]
