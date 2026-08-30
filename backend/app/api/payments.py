from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.negotiation import Negotiation
from app.models.order import Order
from app.models.payment_link import PaymentLink
from app.payments.payment_service import create_order_and_link
from app.services.auth_service import require_role

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class PaymentInitiateRequest(BaseModel):
    negotiation_id: str


@router.post("/initiate", status_code=201)
@limiter.limit("20/minute")
def initiate_payment(request: Request, body: PaymentInitiateRequest,
                     db: Session = Depends(get_db),
                     _: User = Depends(require_role("buyer", "merchant", "admin"))):
    negotiation = db.query(Negotiation).filter(
        Negotiation.negotiation_id == body.negotiation_id
    ).first()
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")

    if negotiation.decision not in ("ALLOWED",) and not (
        negotiation.decision == "APPROVAL_REQUIRED" and not negotiation.requires_human_approval
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Negotiation is not payable (decision={negotiation.decision})",
        )

    return create_order_and_link(db, negotiation)


@router.get("/orders")
def list_orders(skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                _: User = Depends(require_role("merchant", "admin"))):
    rows = db.query(Order).order_by(Order.id.desc()).offset(skip).limit(limit).all()
    return [
        {
            "order_id": r.order_id,
            "negotiation_id": r.negotiation_id,
            "amount": float(r.amount),
            "currency": r.currency,
            "receipt": r.receipt,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in rows
    ]


@router.get("/links")
def list_payment_links(skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                       _: User = Depends(require_role("merchant", "admin"))):
    rows = db.query(PaymentLink).order_by(PaymentLink.id.desc()).offset(skip).limit(limit).all()
    return [
        {
            "link_id": r.link_id,
            "order_id": r.order_id,
            "negotiation_id": r.negotiation_id,
            "short_url": r.short_url,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in rows
    ]
