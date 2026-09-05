import json
import hmac
import hashlib
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.buyer import Buyer
from app.models.product import Product
from app.models.negotiation import Negotiation
from app.services.ai_commerce_service import AICommerceOrchestrator
from app.services.approval_service import decide_approval
from app.payments.payment_service import create_order_and_link
from app.payments.webhook_service import process_webhook_event
from app.services.trust_service import update_trust_score
from app.services.seed_service import seed_all
from app.services.auth_service import get_current_user, require_role
from app.config import settings

router = APIRouter()

orchestrator = AICommerceOrchestrator()


@router.post("/full-flow")
def run_full_demo(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    buyer = db.query(Buyer).filter(Buyer.buyer_id == "BUYER_DEFAULT_001").first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Default buyer not found")

    product = db.query(Product).filter(Product.product_id == "SUB_PRO_001").first()
    if not product:
        raise HTTPException(status_code=404, detail="Default product not found")

    result = orchestrator.run_transaction(
        db, "BUYER_DEFAULT_001", "SUB_PRO_001", 1, 0.18
    )

    approval_id = result.get("approval_id")
    if approval_id:
        decide_approval(db, approval_id, "APPROVED", "demo_admin", "Auto-approval for demo")

    negotiation = db.query(Negotiation).filter(
        Negotiation.negotiation_id == result["negotiation_id"]
    ).first()
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")

    payment = create_order_and_link(db, negotiation)
    order_id = payment["order_id"]
    payment_link = payment.get("payment_link") or payment.get("short_url")

    amount_paise = int(round(float(negotiation.final_amount) * 100))
    webhook_payload = {
        "id": f"evt_demo_{uuid.uuid4().hex[:16]}",
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "order_id": order_id,
                    "amount": amount_paise,
                    "currency": "INR",
                    "status": "captured",
                }
            }
        },
    }

    payload_bytes = json.dumps(webhook_payload, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(
        key=settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()

    process_webhook_event(db, webhook_payload, signature)

    update_trust_score(db, buyer.buyer_id)

    return {
        "status": "success",
        "negotiation_id": result.get("negotiation_id"),
        "approval_id": approval_id,
        "order_id": order_id,
        "payment_link": payment_link,
        "final_status": "paid",
        "message": "Full demo flow completed successfully",
    }


@router.post("/reset")
def reset_demo(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    seed_all(db)
    return {"status": "reset", "message": "Demo data reset successfully"}
