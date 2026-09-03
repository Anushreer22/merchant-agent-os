from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.buyer import Buyer
from app.models.user import User
from app.services.trust_service import calculate_trust_score
from app.services.auth_service import require_role

router = APIRouter()


@router.get("/{buyer_id}/trust-score")
def get_trust_score(
    buyer_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("merchant", "admin")),
):
    buyer = db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return {
        "buyer_id": buyer_id,
        "trust_score": calculate_trust_score(buyer),
        "total_transactions": buyer.total_transactions,
        "successful_transactions": buyer.successful_transactions,
        "on_time_payments": buyer.on_time_payments,
    }
