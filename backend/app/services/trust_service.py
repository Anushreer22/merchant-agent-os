from sqlalchemy.orm import Session
from app.models.buyer import Buyer


def calculate_trust_score(buyer: Buyer) -> float:
    """Score 0-100: 50pts from success rate + 50pts from on-time payment rate."""
    total = buyer.total_transactions or 0
    if total == 0:
        return 0.0
    success_rate = buyer.successful_transactions / total
    on_time_rate = buyer.on_time_payments / total
    return round(min(100.0, success_rate * 50 + on_time_rate * 50), 2)


def update_trust_score_after_payment(db: Session, buyer_id: str, success: bool) -> None:
    buyer = db.query(Buyer).filter(Buyer.buyer_id == buyer_id).first()
    if not buyer:
        return
    buyer.total_transactions = (buyer.total_transactions or 0) + 1
    if success:
        buyer.successful_transactions = (buyer.successful_transactions or 0) + 1
        buyer.on_time_payments = (buyer.on_time_payments or 0) + 1
    buyer.trust_score = calculate_trust_score(buyer)
    db.commit()


def trust_score_discount_bonus(trust_score: float, rules: dict) -> float:
    """Return extra auto-discount allowed for high-trust buyers (configurable in policy rules)."""
    threshold = float(rules.get("trust_score_bonus_threshold", 80))
    bonus = float(rules.get("trust_score_bonus_discount", 0.05))
    return bonus if trust_score >= threshold else 0.0
