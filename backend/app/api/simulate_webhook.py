import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.negotiation import Negotiation
from app.models.webhook_event import WebhookEvent
from app.audit.ledger import append_audit_event
from app.services.invoice_service import generate_invoice_pdf
from app.services.trust_service import update_trust_score_after_payment
from app.services.notification_service import notify
from app.models.buyer import Buyer
from app.models.product import Product
from app.services.trust_service import update_trust_score
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

    neg = db.query(Negotiation).filter(
        Negotiation.negotiation_id == order.negotiation_id
    ).first()
    buyer = db.query(Buyer).filter(Buyer.buyer_id == neg.buyer_id).first() if neg else None
    product = db.query(Product).filter(Product.product_id == neg.product_id).first() if neg else None

    if neg and buyer and product:
        try:
            url = generate_invoice_pdf(db, order, neg, buyer, product)
            if url:
                order.invoice_url = url
        except Exception:
            pass

    webhook_row = WebhookEvent(
        event_id=event_id,
        event_type="payment.captured",
        payload={"simulated": True, "order_id": body.order_id},
        processed=True,
    )
    db.add(webhook_row)
    db.commit()
    if negotiation := db.query(Negotiation).filter(Negotiation.negotiation_id == order.negotiation_id).first():
        if buyer := db.query(Buyer).filter(Buyer.buyer_id == negotiation.buyer_id).first():
            buyer.total_transactions += 1
            buyer.successful_transactions += 1
            buyer.on_time_payments += 1
            db.add(buyer)
            db.commit()
            update_trust_score(db, buyer.buyer_id)

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
        "invoice_url": order.invoice_url or None,
    }
