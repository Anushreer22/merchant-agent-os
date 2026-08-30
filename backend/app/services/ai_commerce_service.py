import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.buyer import Buyer
from app.models.product import Product
from app.agents.buyer_agent import BuyerAgent
from app.services.negotiation_service import create_negotiation
from app.services.approval_service import create_approval

logger = logging.getLogger(__name__)


class AICommerceOrchestrator:
    def run_transaction(
        self,
        db: Session,
        buyer_id: str,
        product_id: str,
        quantity: int,
        desired_discount: float,
    ) -> dict:
        transcript = []

        # --- Load buyer and product ---
        buyer = db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()
        if not buyer:
            raise HTTPException(status_code=404, detail="Buyer not found")

        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        buyer_agent = BuyerAgent(buyer)

        # --- Step 1: Buyer makes initial offer ---
        offer = buyer_agent.make_offer(product, desired_discount)
        transcript.append({
            "step": 1,
            "actor": "buyer_agent",
            "action": "make_offer",
            "detail": {
                "requested_discount": offer["requested_discount"],
                "message": offer["message"],
                "strategy": offer["strategy"],
            },
        })

        # --- Step 2: Directly call negotiation service (bypass LLM intent extraction) ---
        neg_result = create_negotiation(
            db=db,
            buyer_id=buyer_id,
            product_id=product_id,
            quantity=quantity,
            requested_discount=offer["requested_discount"],
        )
        decision = neg_result.get("decision", "REJECTED")
        negotiation_id = neg_result.get("negotiation_id")
        final_price = float(neg_result.get("final_price") or 0.0)
        counter_offer = neg_result.get("counter_offer")
        currency = neg_result.get("currency", "INR")

        transcript.append({
            "step": 2,
            "actor": "merchant_agent",
            "action": "evaluate_offer",
            "detail": {
                "decision": decision,
                "reason_code": neg_result.get("reason_code"),
                "negotiation_id": negotiation_id,
                "final_price": final_price,
                "counter_offer": counter_offer,
            },
        })

        # --- Step 3: REJECTED ---
        if decision == "REJECTED":
            transcript.append({
                "step": 3,
                "actor": "orchestrator",
                "action": "terminate",
                "detail": {"reason": "offer_rejected", "counter_offer": counter_offer},
            })
            return {
                "status": "rejected",
                "negotiation_id": negotiation_id,
                "counter_offer": counter_offer,
                "final_price": final_price,
                "currency": currency,
                "transcript": transcript,
            }

        # --- Step 4: APPROVAL_REQUIRED ---
        if decision == "APPROVAL_REQUIRED":
            approval = None
            approval_id = None
            try:
                approval = create_approval(db, negotiation_id)
                approval_id = approval.approval_id
            except Exception as exc:
                logger.warning("Could not auto-create approval: %s", exc)

            transcript.append({
                "step": 3,
                "actor": "orchestrator",
                "action": "create_approval",
                "detail": {"approval_id": approval_id},
            })
            return {
                "status": "approval_required",
                "negotiation_id": negotiation_id,
                "approval_id": approval_id,
                "final_price": final_price,
                "currency": currency,
                "counter_offer": counter_offer,
                "transcript": transcript,
            }

        # --- Step 5: Budget firewall (ALLOWED path) ---
        if not buyer_agent.check_budget(final_price):
            transcript.append({
                "step": 3,
                "actor": "buyer_agent",
                "action": "budget_check",
                "detail": {"passed": False, "final_price": final_price},
            })
            return {
                "status": "budget_exceeded",
                "negotiation_id": negotiation_id,
                "final_price": final_price,
                "currency": currency,
                "transcript": transcript,
            }

        transcript.append({
            "step": 3,
            "actor": "buyer_agent",
            "action": "budget_check",
            "detail": {"passed": True, "final_price": final_price},
        })

        # --- Step 6: Initiate payment ---
        try:
            payment = buyer_agent.initiate_payment(negotiation_id, db)
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Payment initiation failed: %s", exc)
            raise HTTPException(status_code=502, detail="Payment initiation failed")

        transcript.append({
            "step": 4,
            "actor": "buyer_agent",
            "action": "initiate_payment",
            "detail": {
                "order_id": payment.get("order_id"),
                "short_url": payment.get("short_url"),
            },
        })

        return {
            "status": "payment_pending",
            "negotiation_id": negotiation_id,
            "final_price": final_price,
            "currency": currency,
            "payment": payment,
            "transcript": transcript,
        }
