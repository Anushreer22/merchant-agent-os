import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.agents.buyer_agent import BuyerAgent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_buyer(**kwargs):
    defaults = dict(
        buyer_id="BUYER_001",
        name="Test Buyer",
        budget=10000.0,
        currency="INR",
        max_single_transaction=8000.0,
        preferred_categories=["subscriptions"],
        negotiation_strategy="balanced",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_product(**kwargs):
    defaults = dict(
        product_id="SUB_PRO_001",
        base_price=1000.0,
        currency="INR",
        inventory=50,
        margin_floor=0.30,
        discount_rules={},
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# check_budget tests
# ---------------------------------------------------------------------------

def test_budget_within_both_limits():
    agent = BuyerAgent(make_buyer(budget=10000, max_single_transaction=8000))
    assert agent.check_budget(5000.0) is True


def test_budget_exactly_at_cap():
    agent = BuyerAgent(make_buyer(budget=10000, max_single_transaction=8000))
    assert agent.check_budget(8000.0) is True


def test_budget_exceeds_single_transaction_cap():
    agent = BuyerAgent(make_buyer(budget=10000, max_single_transaction=8000))
    assert agent.check_budget(9000.0) is False


def test_budget_exceeds_total_budget():
    agent = BuyerAgent(make_buyer(budget=5000, max_single_transaction=8000))
    assert agent.check_budget(6000.0) is False


def test_budget_zero_amount():
    agent = BuyerAgent(make_buyer(budget=10000, max_single_transaction=8000))
    assert agent.check_budget(0.0) is True


# ---------------------------------------------------------------------------
# make_offer tests
# ---------------------------------------------------------------------------

def test_make_offer_balanced():
    agent = BuyerAgent(make_buyer(negotiation_strategy="balanced"))
    product = make_product(base_price=1000)
    offer = agent.make_offer(product, desired_discount=0.10)
    assert offer["requested_discount"] == pytest.approx(0.10)
    assert offer["product_id"] == "SUB_PRO_001"
    assert "10.0%" in offer["message"]
    assert offer["strategy"] == "balanced"


def test_make_offer_aggressive_inflates_discount():
    agent = BuyerAgent(make_buyer(negotiation_strategy="aggressive"))
    product = make_product(base_price=1000)
    offer = agent.make_offer(product, desired_discount=0.10)
    # 0.10 * 1.2 = 0.12
    assert offer["requested_discount"] == pytest.approx(0.12)


def test_make_offer_conservative_deflates_discount():
    agent = BuyerAgent(make_buyer(negotiation_strategy="conservative"))
    product = make_product(base_price=1000)
    offer = agent.make_offer(product, desired_discount=0.10)
    # 0.10 * 0.8 = 0.08
    assert offer["requested_discount"] == pytest.approx(0.08)


def test_make_offer_aggressive_capped_at_max():
    # 0.25 * 1.2 = 0.30, but aggressive cap is 0.25
    agent = BuyerAgent(make_buyer(negotiation_strategy="aggressive"))
    product = make_product(base_price=1000)
    offer = agent.make_offer(product, desired_discount=0.25)
    assert offer["requested_discount"] == pytest.approx(0.25)


def test_make_offer_unit_price_calculated():
    agent = BuyerAgent(make_buyer(negotiation_strategy="balanced"))
    product = make_product(base_price=1000)
    offer = agent.make_offer(product, desired_discount=0.10)
    assert offer["unit_price_after_discount"] == pytest.approx(900.0)


# ---------------------------------------------------------------------------
# respond_to_counter_offer tests
# ---------------------------------------------------------------------------

def test_respond_accepts_within_strategy_and_budget():
    agent = BuyerAgent(make_buyer(budget=10000, max_single_transaction=8000, negotiation_strategy="balanced"))
    counter = {"discount": 0.15, "final_unit_price": 850.0}
    assert agent.respond_to_counter_offer(counter, quantity=2) is True  # total=1700 < 8000


def test_respond_rejects_discount_above_strategy_max():
    # conservative max is 0.15; counter offers 0.20
    agent = BuyerAgent(make_buyer(negotiation_strategy="conservative"))
    counter = {"discount": 0.20, "final_unit_price": 800.0}
    assert agent.respond_to_counter_offer(counter, quantity=1) is False


def test_respond_rejects_when_total_exceeds_budget():
    agent = BuyerAgent(make_buyer(budget=1000, max_single_transaction=1000, negotiation_strategy="aggressive"))
    counter = {"discount": 0.10, "final_unit_price": 900.0}
    # total = 900 * 2 = 1800 > 1000
    assert agent.respond_to_counter_offer(counter, quantity=2) is False


def test_respond_accepts_aggressive_up_to_25_pct():
    agent = BuyerAgent(make_buyer(budget=10000, max_single_transaction=10000, negotiation_strategy="aggressive"))
    counter = {"discount": 0.25, "final_unit_price": 750.0}
    assert agent.respond_to_counter_offer(counter, quantity=1) is True


def test_respond_rejects_aggressive_above_25_pct():
    agent = BuyerAgent(make_buyer(budget=10000, max_single_transaction=10000, negotiation_strategy="aggressive"))
    counter = {"discount": 0.30, "final_unit_price": 700.0}
    assert agent.respond_to_counter_offer(counter, quantity=1) is False


# ---------------------------------------------------------------------------
# initiate_payment tests
# ---------------------------------------------------------------------------

def test_initiate_payment_success():
    buyer = make_buyer(budget=10000, max_single_transaction=10000)
    agent = BuyerAgent(buyer)

    neg = SimpleNamespace(
        negotiation_id="neg-001",
        final_amount=900.0,
        buyer_id="BUYER_001",
        policy_version="1.0",
        final_discount=0.10,
        currency="INR",
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = neg

    payment_result = {"order_id": "ord_001", "short_url": "https://rzp.io/l/x", "amount": 900.0}
    with patch("app.agents.buyer_agent.create_order_and_link", return_value=payment_result):
        result = agent.initiate_payment("neg-001", db)

    assert result["order_id"] == "ord_001"


def test_initiate_payment_budget_exceeded_raises_400():
    from fastapi import HTTPException
    buyer = make_buyer(budget=500, max_single_transaction=500)
    agent = BuyerAgent(buyer)

    neg = SimpleNamespace(
        negotiation_id="neg-001",
        final_amount=900.0,
        buyer_id="BUYER_001",
        policy_version="1.0",
        final_discount=0.10,
        currency="INR",
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = neg

    with pytest.raises(HTTPException) as exc:
        agent.initiate_payment("neg-001", db)
    assert exc.value.status_code == 400


def test_initiate_payment_negotiation_not_found_raises_404():
    from fastapi import HTTPException
    agent = BuyerAgent(make_buyer())
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        agent.initiate_payment("missing", db)
    assert exc.value.status_code == 404
