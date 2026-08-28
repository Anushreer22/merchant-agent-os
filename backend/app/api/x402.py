from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.x402_service import get_payment_required_response

router = APIRouter()


@router.get("/payment-required/{negotiation_id}")
def payment_required(negotiation_id: str, db: Session = Depends(get_db)):
    """
    x402-style endpoint. Returns HTTP 402 with a structured payment payload.
    Clients (including AI buyer agents) should parse this and follow the
    payment_link to complete the transaction.
    """
    payload = get_payment_required_response(db, negotiation_id)
    return JSONResponse(status_code=402, content=payload)
