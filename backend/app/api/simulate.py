from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.ai_commerce_service import AICommerceOrchestrator
from app.services.auth_service import require_role

router = APIRouter()
_orchestrator = AICommerceOrchestrator()


class AICommerceRequest(BaseModel):
    buyer_id: str
    product_id: str
    quantity: int = Field(..., gt=0)
    desired_discount: float = Field(..., ge=0.0, le=1.0)


@router.post("/ai-commerce")
async def run_ai_commerce(request: AICommerceRequest, db: Session = Depends(get_db),
                          _: User = Depends(require_role("buyer", "admin"))):
    return _orchestrator.run_transaction(
        db=db,
        buyer_id=request.buyer_id,
        product_id=request.product_id,
        quantity=request.quantity,
        desired_discount=request.desired_discount,
    )
