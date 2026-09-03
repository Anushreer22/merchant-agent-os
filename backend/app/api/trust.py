from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.buyer import Buyer
from app.services.auth_service import require_role

router = APIRouter()

@router.get("/buyers/{buyer_id}/trust-score")
def get_buyer_trust_score(
    buyer_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("merchant", "admin"))
):
    buyer = db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return {
        "buyer_id": buyer.buyer_id,
        "trust_score": buyer.trust_score,
        "total_transactions": buyer.total_transactions,
        "successful_transactions": buyer.successful_transactions,
        "on_time_payments": buyer.on_time_payments,
    }
