from sqlalchemy.orm import Session
from app.payments.payment_service import create_order_and_link
from app.models.negotiation import Negotiation

# Maximum discount the buyer will ever accept per strategy
_MAX_ACCEPT_DISCOUNT = {
    "aggressive": 0.25,
    "balanced": 0.20,
    "conservative": 0.15,
}

# Multiplier applied to desired_discount when making an offer
_OFFER_MULTIPLIER = {
    "aggressive": 1.2,
    "balanced": 1.0,
    "conservative": 0.8,
}


class BuyerAgent:
    def __init__(self, buyer):
        self.buyer = buyer

    # ------------------------------------------------------------------
    # Budget firewall — the merchant can NEVER override this
    # ------------------------------------------------------------------

    def check_budget(self, amount: float) -> bool:
        """Return True only if amount fits within both budget and single-transaction cap."""
        budget = float(self.buyer.budget)
        cap = float(self.buyer.max_single_transaction)
        return amount <= cap and amount <= budget

    # ------------------------------------------------------------------
    # Offer generation
    # ------------------------------------------------------------------

    def make_offer(self, product, desired_discount: float) -> dict:
        """Build a structured offer based on negotiation strategy."""
        strategy = self.buyer.negotiation_strategy
        multiplier = _OFFER_MULTIPLIER.get(strategy, 1.0)
        # Cap the ask at the maximum the buyer would ever accept
        max_accept = _MAX_ACCEPT_DISCOUNT.get(strategy, 0.20)
        ask_discount = min(desired_discount * multiplier, max_accept)
        ask_discount = round(ask_discount, 4)

        base_price = float(product.base_price)
        unit_price_after = base_price * (1 - ask_discount)

        strategy_phrases = {
            "aggressive": f"I'm looking for the best possible deal. Could you offer {ask_discount * 100:.1f}% off?",
            "balanced": f"I'd like to request a {ask_discount * 100:.1f}% discount on this product.",
            "conservative": f"If possible, I'd appreciate a modest {ask_discount * 100:.1f}% discount.",
        }
        message = strategy_phrases.get(
            strategy,
            f"I'd like a {ask_discount * 100:.1f}% discount on {product.product_id}.",
        )

        return {
            "product_id": product.product_id,
            "quantity": 1,
            "requested_discount": ask_discount,
            "unit_price_after_discount": round(unit_price_after, 2),
            "message": message,
            "strategy": strategy,
        }

    # ------------------------------------------------------------------
    # Counter-offer evaluation
    # ------------------------------------------------------------------

    def respond_to_counter_offer(self, counter_offer: dict, quantity: int = 1) -> bool:
        """
        Decide whether to accept a counter-offer.
        Returns True only if:
          - The offered discount is within the buyer's strategy tolerance.
          - The total amount is within budget.
        """
        offered_discount = float(counter_offer.get("discount", 0.0))
        final_unit_price = float(counter_offer.get("final_unit_price", 0.0))
        total = final_unit_price * quantity

        strategy = self.buyer.negotiation_strategy
        max_accept = _MAX_ACCEPT_DISCOUNT.get(strategy, 0.20)

        if offered_discount > max_accept:
            return False
        if not self.check_budget(total):
            return False
        return True

    # ------------------------------------------------------------------
    # Payment initiation
    # ------------------------------------------------------------------

    def initiate_payment(self, negotiation_id: str, db: Session) -> dict:
        """Load the negotiation and create a Razorpay order + payment link."""
        negotiation = db.query(Negotiation).filter(
            Negotiation.negotiation_id == negotiation_id
        ).first()
        if not negotiation:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Negotiation not found")

        total = float(negotiation.final_amount)
        if not self.check_budget(total):
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Final amount {total} exceeds buyer budget or single-transaction limit",
            )

        return create_order_and_link(db, negotiation)
