from sqlalchemy.orm import Session
from app.models.policy import Policy

DEFAULT_RULES = {
    "max_auto_discount": 0.15,
    "max_human_approved_discount": 0.20,
    "margin_floor": 0.30,
    "human_approval_amount": 5000,
    "max_quantity_without_approval": 20,
    "max_retry_count": 2,
}


def get_active_policy(db: Session) -> Policy | None:
    return db.query(Policy).filter(Policy.is_active == True).order_by(Policy.id.desc()).first()


def seed_default_policy(db: Session) -> None:
    if db.query(Policy).count() > 0:
        return
    db.add(Policy(version="1.0", rules=DEFAULT_RULES, is_active=True))
    db.commit()
