from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class NegotiationRequest(BaseModel):
    buyer_id: str
    product_id: str
    quantity: int = Field(..., gt=0)
    requested_discount: float = Field(..., ge=0.0, le=1.0)
    idempotency_key: Optional[str] = None


class NegotiationResponse(BaseModel):
    negotiation_id: str
    decision: str
    requires_human_approval: bool
    maximum_allowed_discount: float
    counter_offer: Optional[Dict[str, Any]]
    policy_version: str
    reason_code: str
    final_price: float
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True
