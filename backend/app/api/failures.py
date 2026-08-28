from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.failure_service import FailureRecoveryService

router = APIRouter()
_svc = FailureRecoveryService()


class NegotiationIdRequest(BaseModel):
    negotiation_id: str


@router.post("/expired-link")
def expired_link(body: NegotiationIdRequest, db: Session = Depends(get_db)):
    return _svc.simulate_expired_payment_link(db, body.negotiation_id)


@router.post("/timeout")
def razorpay_timeout(body: NegotiationIdRequest, db: Session = Depends(get_db)):
    return _svc.simulate_razorpay_timeout(db, body.negotiation_id)
