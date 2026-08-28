from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.agents.merchant_agent import MerchantAgent

router = APIRouter()
_agent = MerchantAgent()


class AgentNegotiateRequest(BaseModel):
    buyer_message: str


@router.post("/negotiate")
def agent_negotiate(request: AgentNegotiateRequest, db: Session = Depends(get_db)):
    return _agent.negotiate(buyer_message=request.buyer_message, db=db)
