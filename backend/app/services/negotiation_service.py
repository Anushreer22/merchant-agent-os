import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.negotiation import Negotiation
from app.services.policy_service import get_active_policy
from app.policy.engine import evaluate_action, _effective_discount_limits, _rules
from app.audit.ledger import append_audit_event


def _build_response(neg: Negotiation, currency: str, counter_offer) -> dict:
    return {
        "negotiation_id": neg.negotiation_id,
        "decision": neg.decision,
        "requires_human_approval": neg.requires_human_approval,
        "maximum_allowed_discount": float(neg.final_discount),
        "counter_offer": counter_offer,
        "policy_version": neg.policy_version,
        "reason_code": neg.reason_code,
        "final_price": float(neg.final_amount),
        "currency": currency,
        "created_at": neg.created_at,
    }


def create_negotiation(
    db: Session,
    buyer_id: str,
    product_id: str,
    quantity: int,
    requested_discount: float,
    idempotency_key: str = None,
) -> dict:
    # Idempotency check
    if idempotency_key:
        existing = db.query(Negotiation).filter(
            Negotiation.idempotency_key == idempotency_key
        ).first()
        if existing:
            product = db.query(Product).filter(Product.product_id == existing.product_id).first()
            currency = product.currency if product else "INR"
            # Reconstruct counter_offer from stored data if needed
            counter_offer = None
            if existing.decision in ("REJECTED", "APPROVAL_REQUIRED"):
                counter_offer = {
                    "discount": float(existing.final_discount),
                    "final_unit_price": round(
                        float(product.base_price) * (1 - float(existing.final_discount)), 2
                    ) if product else 0.0,
                }
            return _build_response(existing, currency, counter_offer)

    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    policy = get_active_policy(db)
    if not policy:
        raise HTTPException(status_code=500, detail="No active policy")

    action = {"product_id": product_id, "quantity": quantity, "requested_discount": requested_discount}
    result = evaluate_action(action, product, policy)

    rules = _rules(policy)
    max_auto, _ = _effective_discount_limits(product, rules)

    # final_discount: the effective discount applied for pricing
    # For ALLOWED: use requested_discount; for others: use maximum_allowed_discount
    if result["decision"] == "ALLOWED":
        final_discount = requested_discount
    else:
        final_discount = result["maximum_allowed_discount"]

    final_unit_price = float(product.base_price) * (1 - final_discount)
    final_amount = final_unit_price * quantity

    neg = Negotiation(
        negotiation_id=str(uuid.uuid4()),
        buyer_id=buyer_id,
        product_id=product_id,
        quantity=quantity,
        requested_discount=requested_discount,
        final_discount=final_discount,
        final_amount=final_amount,
        decision=result["decision"],
        requires_human_approval=result["requires_human_approval"],
        policy_version=result["policy_version"],
        reason_code=result["reason_code"],
        status="PENDING",
        idempotency_key=idempotency_key,
    )
    db.add(neg)
    db.commit()
    db.refresh(neg)

    try:
        append_audit_event(
            db,
            actor="MERCHANT_AGENT",
            action_type="NEGOTIATION_CREATED",
            payload={
                "negotiation_id": neg.negotiation_id,
                "buyer_id": buyer_id,
                "product_id": product_id,
                "quantity": quantity,
                "requested_discount": requested_discount,
                "decision": neg.decision,
            },
            policy_version=neg.policy_version,
            negotiation_id=neg.negotiation_id,
        )
    except Exception:
        pass

    return _build_response(neg, product.currency, result["counter_offer"])
