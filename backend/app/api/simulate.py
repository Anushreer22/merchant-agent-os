from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ai_commerce_service import AICommerceOrchestrator

router = APIRouter()
_orchestrator = AICommerceOrchestrator()


class AICommerceRequest(BaseModel):
    buyer_id: str
    product_id: str
    quantity: int = Field(..., gt=0)
    desired_discount: float = Field(..., ge=0.0, le=1.0)


@router.post("/ai-commerce")
def simulate_ai_commerce(request: AICommerceRequest, db: Session = Depends(get_db)):
    return _orchestrator.run_transaction(
        db=db,
        buyer_id=request.buyer_id,
        product_id=request.product_id,
        quantity=request.quantity,
        desired_discount=request.desired_discount,
    )
