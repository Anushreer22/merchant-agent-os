from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class BuyerCreate(BaseModel):
    buyer_id: str
    name: str
    budget: float = Field(..., gt=0)
    currency: str = "INR"
    max_single_transaction: float = Field(..., gt=0)
    preferred_categories: List[str] = []
    negotiation_strategy: str = "balanced"


class BuyerResponse(BaseModel):
    buyer_id: str
    name: str
    budget: float
    currency: str
    max_single_transaction: float
    preferred_categories: List[str]
    negotiation_strategy: str
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    desired_discount: float = Field(..., ge=0.0, le=1.0)


class PurchaseResponse(BaseModel):
    status: str
    decision: Optional[str] = None
    negotiation_id: Optional[str] = None
    final_price: Optional[float] = None
    currency: Optional[str] = None
    counter_offer: Optional[Dict[str, Any]] = None
    payment: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
