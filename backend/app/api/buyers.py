from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.buyer import Buyer
from app.models.product import Product
from app.schemas.buyer import BuyerCreate, BuyerResponse, PurchaseRequest, PurchaseResponse
from app.agents.buyer_agent import BuyerAgent
from app.services.negotiation_service import create_negotiation
from app.payments.payment_service import create_order_and_link
from app.services.auth_service import require_role
from app.models.negotiation import Negotiation

router = APIRouter()


@router.post("/", response_model=BuyerResponse, status_code=201)
def create_buyer(body: BuyerCreate, db: Session = Depends(get_db),
                 _: User = Depends(require_role("admin"))):
    if db.query(Buyer).filter(Buyer.buyer_id == body.buyer_id).first():
        raise HTTPException(status_code=409, detail="Buyer already exists")
    buyer = Buyer(**body.model_dump())
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


@router.get("/{buyer_id}", response_model=BuyerResponse)
def get_buyer(buyer_id: str, db: Session = Depends(get_db),
              _: User = Depends(require_role("buyer", "admin"))):
    buyer = db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return buyer


@router.post("/{buyer_id}/purchase", response_model=PurchaseResponse)
def purchase(buyer_id: str, body: PurchaseRequest, db: Session = Depends(get_db),
             _: User = Depends(require_role("buyer", "admin"))):
    buyer = db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    product = db.query(Product).filter(Product.product_id == body.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    agent = BuyerAgent(buyer)

    neg_result = create_negotiation(
        db=db,
        buyer_id=buyer.buyer_id,
        product_id=body.product_id,
        quantity=body.quantity,
        requested_discount=body.desired_discount,
    )

    decision = neg_result["decision"]
    final_price = neg_result["final_price"]

    if decision == "REJECTED":
        return PurchaseResponse(
            status="rejected",
            decision=decision,
            negotiation_id=neg_result["negotiation_id"],
            counter_offer=neg_result.get("counter_offer"),
            message=f"Offer rejected: {neg_result['reason_code']}",
        )

    if not agent.check_budget(final_price):
        return PurchaseResponse(
            status="budget_exceeded",
            decision=decision,
            negotiation_id=neg_result["negotiation_id"],
            final_price=final_price,
            currency=neg_result["currency"],
            message="Offer exceeds buyer budget",
        )

    if decision == "APPROVAL_REQUIRED":
        return PurchaseResponse(
            status="approval_required",
            decision=decision,
            negotiation_id=neg_result["negotiation_id"],
            final_price=final_price,
            currency=neg_result["currency"],
            counter_offer=neg_result.get("counter_offer"),
            message="Negotiation requires human approval before payment can proceed",
        )

    negotiation_row = db.query(Negotiation).filter(
        Negotiation.negotiation_id == neg_result["negotiation_id"]
    ).first()
    payment = create_order_and_link(db, negotiation_row)

    return PurchaseResponse(
        status="payment_initiated",
        decision=decision,
        negotiation_id=neg_result["negotiation_id"],
        final_price=final_price,
        currency=neg_result["currency"],
        payment=payment,
        message="Payment initiated successfully",
    )
