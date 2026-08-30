import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.payment_link import PaymentLink
from app.payments.razorpay_client import get_razorpay_client
from app.audit.ledger import append_audit_event

logger = logging.getLogger(__name__)


def create_order_and_link(db: Session, negotiation, idempotency_key: str = None) -> dict:
    # Idempotency: return existing order+link if already created for this negotiation
    existing_order = db.query(Order).filter(
        Order.negotiation_id == negotiation.negotiation_id
    ).first()
    if existing_order:
        existing_link = db.query(PaymentLink).filter(
            PaymentLink.order_id == existing_order.order_id
        ).first()
        return {
            "order_id": existing_order.order_id,
            "payment_link": existing_link.link_id if existing_link else None,
            "short_url": existing_link.short_url if existing_link else None,
            "amount": float(existing_order.amount),
            "currency": existing_order.currency,
        }

    amount_rupees = float(negotiation.final_amount)
    # Razorpay expects amount in paise (smallest currency unit)
    amount_paise = int(round(amount_rupees * 100))
    currency = getattr(negotiation, "currency", "INR") or "INR"
    receipt = f"rcpt_{negotiation.negotiation_id[:35]}"

    metadata = {
        "negotiation_id": negotiation.negotiation_id,
        "policy_version": negotiation.policy_version,
        "discount_applied": float(negotiation.final_discount),
        "buyer_id": negotiation.buyer_id,
        "merchant_id": "MERCHANT_001",
    }

    client = get_razorpay_client()

    try:
        rzp_order = client.order.create({
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt,
            "notes": metadata,
        })
    except Exception as exc:
        logger.error("Razorpay order creation failed: %s", exc)
        raise HTTPException(status_code=502, detail="Payment provider error")

    try:
        rzp_link = client.payment_link.create({
            "amount": amount_paise,
            "currency": currency,
            "description": f"Payment for negotiation {negotiation.negotiation_id}",
            "reference_id": receipt,
            "notes": metadata,
        })
    except Exception as exc:
        logger.error("Razorpay payment link creation failed: %s", exc)
        raise HTTPException(status_code=502, detail="Payment provider error")

    order = Order(
        order_id=rzp_order["id"],
        negotiation_id=negotiation.negotiation_id,
        amount=amount_rupees,
        currency=currency,
        receipt=receipt,
        status=rzp_order.get("status", "created"),
        metadata_json=metadata,
    )
    db.add(order)

    link = PaymentLink(
        link_id=rzp_link["id"],
        order_id=rzp_order["id"],
        negotiation_id=negotiation.negotiation_id,
        short_url=rzp_link.get("short_url", ""),
        status=rzp_link.get("status", "created"),
    )
    db.add(link)
    db.commit()
    db.refresh(order)
    db.refresh(link)

    try:
        append_audit_event(
            db,
            actor="SYSTEM",
            action_type="ORDER_CREATED",
            payload={
                "order_id": order.order_id,
                "negotiation_id": negotiation.negotiation_id,
                "amount": amount_rupees,
                "currency": currency,
            },
            negotiation_id=negotiation.negotiation_id,
            razorpay_entity_id=order.order_id,
        )
    except Exception:
        pass

    return {
        "order_id": order.order_id,
        "payment_link": link.link_id,
        "short_url": link.short_url,
        "amount": float(order.amount),
        "currency": order.currency,
    }
