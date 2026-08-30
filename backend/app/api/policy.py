from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.policy_service import get_active_policy
from app.services.auth_service import require_role

router = APIRouter()


@router.get("/")
def read_policy(db: Session = Depends(get_db),
                _: User = Depends(require_role("merchant", "admin"))):
    policy = get_active_policy(db)
    if not policy:
        raise HTTPException(status_code=404, detail="No active policy found")
    return {
        "version": policy.version,
        "rules": policy.rules,
        "is_active": policy.is_active,
        "created_at": policy.created_at,
    }
