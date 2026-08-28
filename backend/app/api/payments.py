from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.negotiation import Negotiation
from app.payments.payment_service import create_order_and_link

router = APIRouter()


class PaymentInitiateRequest(BaseModel):
    negotiation_id: str


@router.post("/initiate", status_code=201)
def initiate_payment(request: PaymentInitiateRequest, db: Session = Depends(get_db)):
    negotiation = db.query(Negotiation).filter(
        Negotiation.negotiation_id == request.negotiation_id
    ).first()
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")

    # Only ALLOWED negotiations (or APPROVAL_REQUIRED that has been approved) can proceed
    if negotiation.decision not in ("ALLOWED",) and not (
        negotiation.decision == "APPROVAL_REQUIRED" and not negotiation.requires_human_approval
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Negotiation is not payable (decision={negotiation.decision})",
        )

    return create_order_and_link(db, negotiation)
