from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import require_role

router = APIRouter()

# In-memory merchant registry (backed by User.merchant_id field on user records)
# For a full implementation, a Merchant table would be added via migration.
# This endpoint manages merchant metadata stored in a simple dict for demo.
_MERCHANTS: dict[str, dict] = {
    "MERCHANT_DEFAULT_001": {
        "merchant_id": "MERCHANT_DEFAULT_001",
        "name": "Default Merchant",
        "email": "merchant@example.com",
    }
}


class MerchantCreate(BaseModel):
    merchant_id: str
    name: str
    email: str


@router.post("/", status_code=201)
def create_merchant(
    body: MerchantCreate,
    _: User = Depends(require_role("admin")),
):
    if body.merchant_id in _MERCHANTS:
        raise HTTPException(status_code=409, detail="Merchant already exists")
    _MERCHANTS[body.merchant_id] = body.model_dump()
    return _MERCHANTS[body.merchant_id]


@router.get("/")
def list_merchants(_: User = Depends(require_role("admin"))):
    return list(_MERCHANTS.values())


@router.get("/{merchant_id}")
def get_merchant(merchant_id: str, _: User = Depends(require_role("merchant", "admin"))):
    m = _MERCHANTS.get(merchant_id)
    if not m:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return m
