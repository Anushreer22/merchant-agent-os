import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.models.negotiation import Negotiation
from app.models.order import Order
from app.models.payment_link import PaymentLink
from app.payments.razorpay_client import get_razorpay_client
from app.payments.payment_service import create_order_and_link
from app.audit.ledger import append_audit_event

logger = logging.getLogger(__name__)


class FailureRecoveryService:

    def simulate_expired_payment_link(self, db: Session, negotiation_id: str) -> dict:
        negotiation = db.query(Negotiation).filter(
            Negotiation.negotiation_id == negotiation_id
        ).first()
        if not negotiation:
            raise HTTPException(status_code=404, detail="Negotiation not found")

        # Find the most recent active payment link for this negotiation
        link = (
            db.query(PaymentLink)
            .filter(
                PaymentLink.negotiation_id == negotiation_id,
                PaymentLink.status == "created",
            )
            .order_by(PaymentLink.id.desc())
            .first()
        )
        if not link:
            raise HTTPException(status_code=404, detail="No active payment link found")

        # Mark link as expired
        link.status = "expired"
        db.commit()

        # Attempt to cancel the associated Razorpay order
        order = db.query(Order).filter(Order.order_id == link.order_id).first()
        if order:
            try:
                client = get_razorpay_client()
                client.order.cancel(order.order_id)
            except Exception as exc:
                logger.warning("Could not cancel Razorpay order %s: %s", order.order_id, exc)

        # Create a fresh order + link with a new idempotency key so the
        # existing-order idempotency guard in create_order_and_link is bypassed.
        # We temporarily clear the cached order by using a unique receipt suffix.
        ts = int(datetime.now(timezone.utc).timestamp())
        new_idempotency_key = f"{negotiation_id}-renewed-{ts}"

        # create_order_and_link checks for an existing Order by negotiation_id.
        # Since one already exists we need to call Razorpay directly here and
        # persist a new Order + PaymentLink row.
        amount_rupees = float(negotiation.final_amount)
        amount_paise = int(round(amount_rupees * 100))
        currency = getattr(negotiation, "currency", "INR") or "INR"
        receipt = f"rcpt_{negotiation_id}_r{ts}"
        metadata = {
            "negotiation_id": negotiation_id,
            "policy_version": negotiation.policy_version,
            "discount_applied": float(negotiation.final_discount),
            "buyer_id": negotiation.buyer_id,
            "renewal": True,
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
            logger.error("Razorpay order creation failed during renewal: %s", exc)
            raise HTTPException(status_code=502, detail="Payment provider error")

        try:
            rzp_link = client.payment_link.create({
                "amount": amount_paise,
                "currency": currency,
                "description": f"Renewed payment for negotiation {negotiation_id}",
                "reference_id": receipt,
                "notes": metadata,
            })
        except Exception as exc:
            logger.error("Razorpay payment link creation failed during renewal: %s", exc)
            raise HTTPException(status_code=502, detail="Payment provider error")

        new_order = Order(
            order_id=rzp_order["id"],
            negotiation_id=negotiation_id,
            amount=amount_rupees,
            currency=currency,
            receipt=receipt,
            status=rzp_order.get("status", "created"),
            metadata_json=metadata,
        )
        db.add(new_order)

        new_link = PaymentLink(
            link_id=rzp_link["id"],
            order_id=rzp_order["id"],
            negotiation_id=negotiation_id,
            short_url=rzp_link.get("short_url", ""),
            status=rzp_link.get("status", "created"),
        )
        db.add(new_link)
        db.commit()
        db.refresh(new_order)
        db.refresh(new_link)

        try:
            append_audit_event(
                db,
                actor="SYSTEM",
                action_type="PAYMENT_LINK_RENEWED",
                payload={
                    "negotiation_id": negotiation_id,
                    "expired_link_id": link.link_id,
                    "new_order_id": new_order.order_id,
                    "new_link_id": new_link.link_id,
                    "idempotency_key": new_idempotency_key,
                },
                negotiation_id=negotiation_id,
                razorpay_entity_id=new_order.order_id,
            )
        except Exception:
            pass

        return {
            "message": "Payment link renewed successfully",
            "expired_link_id": link.link_id,
            "order_id": new_order.order_id,
            "payment_link": new_link.link_id,
            "short_url": new_link.short_url,
            "amount": float(new_order.amount),
            "currency": new_order.currency,
            "idempotency_key": new_idempotency_key,
        }

    def simulate_razorpay_timeout(self, db: Session, negotiation_id: str) -> dict:
        negotiation = db.query(Negotiation).filter(
            Negotiation.negotiation_id == negotiation_id
        ).first()
        if not negotiation:
            raise HTTPException(status_code=404, detail="Negotiation not found")

        limit = settings.PAYMENT_RETRY_LIMIT
        last_exc = None

        for attempt in range(1, limit + 2):  # attempts: 1 … limit+1
            try:
                client = get_razorpay_client()
                # Simulate a timeout by calling a lightweight probe; in tests
                # the client is mocked to raise TimeoutError on demand.
                client.order.all({"count": 1})
                # Success path
                try:
                    append_audit_event(
                        db,
                        actor="SYSTEM",
                        action_type="PAYMENT_TIMEOUT_RECOVERED",
                        payload={
                            "negotiation_id": negotiation_id,
                            "attempts": attempt,
                        },
                        negotiation_id=negotiation_id,
                    )
                except Exception:
                    pass
                return {"status": "recovered", "attempts": attempt, "negotiation_id": negotiation_id}

            except (TimeoutError, Exception) as exc:
                last_exc = exc
                logger.warning(
                    "Razorpay timeout simulation attempt %d/%d: %s",
                    attempt, limit + 1, exc,
                )
                if attempt > limit:
                    break

        # All attempts exhausted
        try:
            append_audit_event(
                db,
                actor="SYSTEM",
                action_type="PAYMENT_TIMEOUT_FAILED",
                payload={
                    "negotiation_id": negotiation_id,
                    "attempts": limit + 1,
                    "error": str(last_exc),
                },
                negotiation_id=negotiation_id,
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=502,
            detail=f"Payment provider timeout after {limit + 1} attempts",
        )
