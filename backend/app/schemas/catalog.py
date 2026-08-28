from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class UpsellOption(BaseModel):
    product_id: str
    bundle_discount: float

class ProductOut(BaseModel):
    product_id: str
    name: str
    description: str
    category: str
    base_price: float
    currency: str
    inventory: int
    margin_floor: float
    discount_rules: Dict[str, Any]
    volume_discount_rules: Dict[str, Any]
    bundle_rules: Dict[str, Any]
    upsell_options: List[UpsellOption]
    availability: bool
    metadata: Dict[str, Any]

    class Config:
        orm_mode = True

class CatalogResponse(BaseModel):
    version: str
    products: List[ProductOut]
    active: bool
    created_at: Optional[datetime] = None
