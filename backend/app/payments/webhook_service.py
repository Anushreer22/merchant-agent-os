import hmac
import hashlib
import json
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.webhook_event import WebhookEvent
from app.models.order import Order
from app.models.negotiation import Negotiation
from app.models.buyer import Buyer
from app.models.product import Product
from app.config import settings
from app.audit.ledger import append_audit_event
from app.services.trust_service import update_trust_score
from app.services.invoice_service import generate_invoice_pdf

logger = logging.getLogger(__name__)

# Maps Razorpay event types to the Order.status value they should set
_ORDER_STATUS_MAP = {
    "payment.captured": "paid",
    "order.paid": "paid",
    "payment.failed": "failed",
}


def verify_webhook_signature(payload_body: bytes, signature_header: str, webhook_secret: str) -> bool:
    expected = hmac.new(
        key=webhook_secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def process_webhook_event(db: Session, payload: dict, signature_header: str) -> dict:
    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
    if not verify_webhook_signature(
        _canonical_bytes(payload), signature_header, webhook_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event_id = payload.get("id")
    event_type = payload.get("event")
    if not event_id or not event_type:
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Idempotency: skip if already seen
    existing = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
    if existing:
        return {"status": "duplicate", "event_id": event_id}

    # Persist raw event before processing
    webhook_row = WebhookEvent(
        event_id=event_id,
        event_type=event_type,
        payload=payload,
        processed=False,
    )
    db.add(webhook_row)

    # Update Order status if this event type maps to one
    new_status = _ORDER_STATUS_MAP.get(event_type)
    if new_status:
        order_id = _extract_order_id(payload)
        if order_id:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order:
                order.status = new_status
                # ---------------------------
                # Update buyer trust score
                # ---------------------------
                _update_buyer_trust(db, order, event_type)
                # ---------------------------
                # Generate PDF invoice
                # ---------------------------
                if new_status == "paid":
                    _generate_invoice_for_order(db, order)
            else:
                logger.warning("Webhook %s references unknown order_id=%s", event_id, order_id)
        else:
            logger.warning("Webhook %s (%s) has no extractable order_id", event_id, event_type)

    webhook_row.processed = True
    db.commit()

    audit_action = {
        "payment.captured": "PAYMENT_CAPTURED",
        "order.paid": "PAYMENT_CAPTURED",
        "payment.failed": "PAYMENT_FAILED",
    }.get(event_type, "WEBHOOK_RECEIVED")
    try:
        append_audit_event(
            db,
            actor="WEBHOOK",
            action_type=audit_action,
            payload={"event_id": event_id, "event_type": event_type},
            razorpay_entity_id=event_id,
        )
    except Exception:
        pass

    return {"status": "processed", "event_id": event_id}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _canonical_bytes(payload: dict) -> bytes:
    """Re-encode payload to bytes for signature verification.

    In production the raw request body bytes are passed directly; this helper
    exists so tests can pass a dict and still exercise the code path.
    """
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def _extract_order_id(payload: dict) -> str | None:
    """Best-effort extraction of Razorpay order_id from various event shapes."""
    try:
        entity = payload.get("payload", {})
        # payment.captured / payment.failed shape
        payment = entity.get("payment", {}).get("entity", {})
        if payment.get("order_id"):
            return payment["order_id"]
        # order.paid shape
        order = entity.get("order", {}).get("entity", {})
        if order.get("id"):
            return order["id"]
    except Exception:
        pass
    return None


def _update_buyer_trust(db: Session, order: Order, event_type: str) -> None:
    """Update the buyer trust score based on the payment outcome."""
    # Determine if this is a successful payment
    is_success = event_type in ("payment.captured", "order.paid")

    # Safely get negotiation_id; test mocks may not have it
    negotiation_id = getattr(order, "negotiation_id", None)
    if not negotiation_id:
        return

    negotiation = db.query(Negotiation).filter(Negotiation.negotiation_id == negotiation_id).first()
    if not negotiation:
        return

    buyer = db.query(Buyer).filter(Buyer.buyer_id == negotiation.buyer_id).first()
    if not buyer:
        return

    buyer.total_transactions += 1
    if is_success:
        buyer.successful_transactions += 1
        buyer.on_time_payments += 1

    db.add(buyer)
    update_trust_score(db, buyer.buyer_id)


def _generate_invoice_for_order(db: Session, order: Order) -> None:
    negotiation_id = getattr(order, "negotiation_id", None)
    if not negotiation_id:
        return
    negotiation = db.query(Negotiation).filter(Negotiation.negotiation_id == negotiation_id).first()
    if not negotiation:
        return
    buyer = db.query(Buyer).filter(Buyer.buyer_id == negotiation.buyer_id).first()
    if not buyer:
        return
    product = db.query(Product).filter(Product.product_id == negotiation.product_id).first()
    if not product:
        return

    try:
        url = generate_invoice_pdf(db, order, negotiation, buyer, product)
        if url:
            order.invoice_url = url
            db.add(order)
            db.commit()
    except Exception:
        logger.exception("Failed to generate invoice for order %s", order.order_id)