# x402-style payment required flow.
# Not full x402 protocol compliance — returns a structured 402 payload
# that clients (including the BuyerAgent) can act on directly.

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.negotiation import Negotiation
from app.models.order import Order
from app.models.payment_link import PaymentLink
from app.payments.payment_service import create_order_and_link

_PAYABLE_DECISIONS = {"ALLOWED", "APPROVAL_REQUIRED"}
_PAYABLE_STATUSES = {"ALLOWED", "APPROVED", "PENDING"}


def get_payment_required_response(db: Session, negotiation_id: str) -> dict:
    """
    Return an x402-style payment-required payload for the given negotiation.

    The caller is responsible for surfacing this as an HTTP 402 response.
    Raises HTTPException 404 if negotiation not found, 400 if not payable.
    """
    negotiation = db.query(Negotiation).filter(
        Negotiation.negotiation_id == negotiation_id
    ).first()
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")

    # A negotiation is payable when the policy allowed it (ALLOWED decision)
    # or when it required human approval and was subsequently APPROVED.
    decision = negotiation.decision
    status = negotiation.status

    payable = (decision == "ALLOWED") or (
        decision == "APPROVAL_REQUIRED" and status == "APPROVED"
    )
    if not payable:
        raise HTTPException(
            status_code=400,
            detail="Payment not allowed yet: negotiation decision is not payable",
        )

    # Reuse existing order + link if already created
    order = db.query(Order).filter(
        Order.negotiation_id == negotiation_id
    ).first()

    if order:
        link = db.query(PaymentLink).filter(
            PaymentLink.order_id == order.order_id
        ).first()
        short_url = link.short_url if link else None
        link_id = link.link_id if link else None
    else:
        result = create_order_and_link(db, negotiation)
        order = db.query(Order).filter(
            Order.negotiation_id == negotiation_id
        ).first()
        link = db.query(PaymentLink).filter(
            PaymentLink.order_id == order.order_id
        ).first() if order else None
        short_url = result.get("short_url")
        link_id = result.get("payment_link")

    return {
        "status": 402,
        "payment_required": True,
        "payment_provider": "razorpay",
        "payment_link": short_url,
        "payment_link_id": link_id,
        "amount": float(negotiation.final_amount),
        "currency": getattr(negotiation, "currency", None) or "INR",
        "order_id": order.order_id if order else None,
        "negotiation_id": negotiation_id,
    }
