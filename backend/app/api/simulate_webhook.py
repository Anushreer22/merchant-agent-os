import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.webhook_event import WebhookEvent
from app.audit.ledger import append_audit_event

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

    # Idempotency: skip if a simulated event already processed this order
    existing = db.query(WebhookEvent).filter(
        WebhookEvent.event_id == event_id
    ).first()
    if existing:
        return {"status": "duplicate", "event_id": event_id}

    # Update order status
    order.status = "paid"

    webhook_row = WebhookEvent(
        event_id=event_id,
        event_type="payment.captured",
        payload={"simulated": True, "order_id": body.order_id},
        processed=True,
    )
    db.add(webhook_row)
    db.commit()

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

    return {"status": "processed", "event_id": event_id, "order_id": body.order_id}
