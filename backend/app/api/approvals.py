from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.approval import ApprovalCreate, ApprovalDecision, ApprovalResponse
from app.services.approval_service import create_approval, decide_approval, get_approval
from app.services.auth_service import require_role, get_current_user
from app.models.approval import Approval

router = APIRouter()


@router.post("/", response_model=ApprovalResponse, status_code=201)
def create(body: ApprovalCreate, db: Session = Depends(get_db),
           _: User = Depends(require_role("merchant", "admin"))):
    return create_approval(db, body.negotiation_id)


@router.post("/{approval_id}/decide", response_model=ApprovalResponse)
def decide(approval_id: str, body: ApprovalDecision, db: Session = Depends(get_db),
           _: User = Depends(require_role("merchant", "admin"))):
    return decide_approval(db, approval_id, body.decision, body.human_user_id, body.reason)


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get(approval_id: str, db: Session = Depends(get_db),
        _: User = Depends(get_current_user)):
    return get_approval(db, approval_id)


@router.get("/")
def list_approvals(skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                   _: User = Depends(require_role("merchant", "admin"))):
    rows = db.query(Approval).order_by(Approval.id.desc()).offset(skip).limit(limit).all()
    return [
        {
            "approval_id": r.approval_id,
            "negotiation_id": r.negotiation_id,
            "buyer_id": r.buyer_id,
            "product_id": r.product_id,
            "quantity": r.quantity,
            "requested_discount": float(r.requested_discount),
            "proposed_discount": float(r.proposed_discount),
            "final_price": float(r.final_price),
            "status": r.status,
            "policy_version": r.policy_version,
            "reason_code": r.reason_code,
            "human_user_id": r.human_user_id,
            "approval_reason": r.approval_reason,
            "created_at": r.created_at,
            "decided_at": r.decided_at,
        }
        for r in rows
    ]
