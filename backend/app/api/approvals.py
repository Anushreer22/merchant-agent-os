from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.approval import ApprovalCreate, ApprovalDecision, ApprovalResponse
from app.services.approval_service import create_approval, decide_approval, get_approval

router = APIRouter()


@router.post("/", response_model=ApprovalResponse, status_code=201)
def create(body: ApprovalCreate, db: Session = Depends(get_db)):
    return create_approval(db, body.negotiation_id)


@router.post("/{approval_id}/decide", response_model=ApprovalResponse)
def decide(approval_id: str, body: ApprovalDecision, db: Session = Depends(get_db)):
    return decide_approval(db, approval_id, body.decision, body.human_user_id, body.reason)


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get(approval_id: str, db: Session = Depends(get_db)):
    return get_approval(db, approval_id)
