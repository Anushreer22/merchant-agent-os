from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.negotiation import NegotiationRequest, NegotiationResponse
from app.services.negotiation_service import create_negotiation

router = APIRouter()


@router.post("/", response_model=NegotiationResponse)
def negotiate(request: NegotiationRequest, db: Session = Depends(get_db)):
    return create_negotiation(
        db=db,
        buyer_id=request.buyer_id,
        product_id=request.product_id,
        quantity=request.quantity,
        requested_discount=request.requested_discount,
        idempotency_key=request.idempotency_key,
    )
