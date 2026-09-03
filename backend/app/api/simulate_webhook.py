import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.negotiation import Negotiation
from app.models.webhook_event import WebhookEvent
from app.audit.ledger import append_audit_event
from app.services.invoice_service import generate_invoice
from app.services.trust_service import update_trust_score_after_payment
from app.services.notification_service import notify

router = APIRouter()


class SimulateWebhookRequest(BaseModel):
    order_id: str


@router.post("/webhook", status_code=200)
def simulate_webhook(body: SimulateWebhookRequest, db: Session = Depends(get_db)):
    """Simulate a payment.captured webhook for demo/testing — no signature required."""
    order = db.query(Order).filter(Order.order_id == body.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    event_id = f"evt_sim_{uuid.uuid4().hex[:16]}"
    order.status = "paid"

    # Generate invoice
    neg = db.query(Negotiation).filter(
        Negotiation.negotiation_id == order.negotiation_id
    ).first()
    order_data = {
        "buyer_id": neg.buyer_id if neg else "—",
        "product_id": neg.product_id if neg else "—",
        "quantity": neg.quantity if neg else 1,
        "discount": float(neg.final_discount) if neg else 0.0,
        "amount": float(order.amount),
        "currency": order.currency,
        "status": "paid",
    }
    invoice_url = generate_invoice(body.order_id, order_data)
    if invoice_url:
        order.invoice_url = invoice_url

    webhook_row = WebhookEvent(
        event_id=event_id,
        event_type="payment.captured",
        payload={"simulated": True, "order_id": body.order_id},
        processed=True,
    )
    db.add(webhook_row)
    db.commit()

    # Update buyer trust score
    if neg:
        try:
            update_trust_score_after_payment(db, neg.buyer_id, success=True)
        except Exception:
            pass

    try:
        append_audit_event(
            db,
            actor="SIMULATE",
            action_type="PAYMENT_CAPTURED",
            payload={"event_id": event_id, "order_id": body.order_id, "simulated": True},
            razorpay_entity_id=body.order_id,
        )
    except Exception:
        pass

    notify({"type": "PAYMENT_CAPTURED", "order_id": body.order_id, "amount": float(order.amount)})

    return {
        "status": "processed",
        "event_id": event_id,
        "order_id": body.order_id,
        "invoice_url": invoice_url or None,
    }
