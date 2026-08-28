from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApprovalCreate(BaseModel):
    negotiation_id: str


class ApprovalDecision(BaseModel):
    decision: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    human_user_id: str
    reason: Optional[str] = None


class ApprovalResponse(BaseModel):
    approval_id: str
    negotiation_id: str
    buyer_id: str
    product_id: str
    quantity: int
    requested_discount: float
    proposed_discount: float
    final_price: float
    margin_after_discount: Optional[float]
    policy_version: str
    reason_code: str
    status: str
    human_user_id: Optional[str]
    approval_reason: Optional[str]
    created_at: datetime
    decided_at: Optional[datetime]

    class Config:
        from_attributes = True
