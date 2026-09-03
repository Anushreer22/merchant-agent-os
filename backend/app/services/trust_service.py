from sqlalchemy.orm import Session
from app.models.buyer import Buyer

def calculate_trust_score(buyer: Buyer) -> float:
    if buyer.total_transactions == 0:
        return 0.0
    success_rate = buyer.successful_transactions / buyer.total_transactions
    on_time_rate = buyer.on_time_payments / max(buyer.total_transactions, 1)
    score = success_rate * 50 + on_time_rate * 50
    return round(min(score, 100.0), 2)

def update_trust_score(db: Session, buyer_id: str):
    buyer = db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()
    if not buyer:
        return
    buyer.trust_score = calculate_trust_score(buyer)
    db.add(buyer)
    db.commit()

def update_trust_score_after_payment(db: Session, buyer_id: str, success: bool = True):
    buyer = db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()
    if not buyer:
        return
    buyer.total_transactions += 1
    if success:
        buyer.successful_transactions += 1
        buyer.on_time_payments += 1
    buyer.trust_score = calculate_trust_score(buyer)
    db.add(buyer)
    db.commit()
