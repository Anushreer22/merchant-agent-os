import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.services.x402_service import get_payment_required_response

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_negotiation(
    negotiation_id="NEG-001",
    decision="ALLOWED",
    status="PENDING",
    final_amount=9000.0,
    final_discount=0.10,
    policy_version="1.0",
    buyer_id="BUYER-001",
):
    return SimpleNamespace(
        negotiation_id=negotiation_id,
        decision=decision,
        status=status,
        final_amount=final_amount,
        final_discount=final_discount,
        policy_version=policy_version,
        buyer_id=buyer_id,
        currency="INR",
    )


def _make_order(order_id="ORD-001", negotiation_id="NEG-001"):
    return SimpleNamespace(
        order_id=order_id,
        negotiation_id=negotiation_id,
        amount=9000.0,
        currency="INR",
        status="created",
    )


def _make_link(link_id="LINK-001", order_id="ORD-001", short_url="https://rzp.io/l/test"):
    return SimpleNamespace(
        link_id=link_id,
        order_id=order_id,
        short_url=short_url,
        status="created",
    )


def _make_db(negotiation=None, order=None, link=None):
    db = MagicMock()

    def query_side(model):
        from app.models.negotiation import Negotiation
        from app.models.order import Order
        from app.models.payment_link import PaymentLink

        q = MagicMock()
        f = MagicMock()

        if model is Negotiation:
            f.first.return_value = negotiation
        elif model is Order:
            f.first.return_value = order
        elif model is PaymentLink:
            f.first.return_value = link

        q.filter.return_value = f
        return q

    db.query.side_effect = query_side
    return db


# ---------------------------------------------------------------------------
# get_payment_required_response — unit tests
# ---------------------------------------------------------------------------

def test_404_when_negotiation_missing():
    db = _make_db(negotiation=None)
    with pytest.raises(HTTPException) as exc:
        get_payment_required_response(db, "MISSING")
    assert exc.value.status_code == 404


def test_400_when_decision_rejected():
    neg = _make_negotiation(decision="REJECTED", status="PENDING")
    db = _make_db(negotiation=neg)
    with pytest.raises(HTTPException) as exc:
        get_payment_required_response(db, "NEG-001")
    assert exc.value.status_code == 400
    assert "not payable" in exc.value.detail.lower()


def test_400_when_approval_required_but_not_yet_approved():
    neg = _make_negotiation(decision="APPROVAL_REQUIRED", status="PENDING")
    db = _make_db(negotiation=neg)
    with pytest.raises(HTTPException) as exc:
        get_payment_required_response(db, "NEG-001")
    assert exc.value.status_code == 400


def test_returns_correct_payload_when_order_exists():
    neg = _make_negotiation(decision="ALLOWED", status="PENDING")
    order = _make_order()
    link = _make_link()
    db = _make_db(negotiation=neg, order=order, link=link)

    result = get_payment_required_response(db, "NEG-001")

    assert result["status"] == 402
    assert result["payment_required"] is True
    assert result["payment_provider"] == "razorpay"
    assert result["order_id"] == "ORD-001"
    assert result["payment_link"] == "https://rzp.io/l/test"
    assert result["payment_link_id"] == "LINK-001"
    assert result["amount"] == 9000.0
    assert result["currency"] == "INR"
    assert result["negotiation_id"] == "NEG-001"


def test_creates_order_when_none_exists():
    neg = _make_negotiation(decision="ALLOWED", status="PENDING")
    order = _make_order()
    link = _make_link()

    # First call to Order query returns None (no existing order),
    # subsequent calls return the newly created order.
    call_count = {"n": 0}
    db = MagicMock()

    def query_side(model):
        from app.models.negotiation import Negotiation
        from app.models.order import Order
        from app.models.payment_link import PaymentLink

        q = MagicMock()
        f = MagicMock()

        if model is Negotiation:
            f.first.return_value = neg
        elif model is Order:
            call_count["n"] += 1
            # First query: no existing order; second query: order created
            f.first.return_value = None if call_count["n"] == 1 else order
        elif model is PaymentLink:
            f.first.return_value = link

        q.filter.return_value = f
        return q

    db.query.side_effect = query_side

    mock_result = {
        "order_id": "ORD-001",
        "payment_link": "LINK-001",
        "short_url": "https://rzp.io/l/test",
        "amount": 9000.0,
        "currency": "INR",
    }

    with patch("app.services.x402_service.create_order_and_link", return_value=mock_result):
        result = get_payment_required_response(db, "NEG-001")

    assert result["order_id"] == "ORD-001"
    assert result["payment_required"] is True


def test_approved_negotiation_is_payable():
    neg = _make_negotiation(decision="APPROVAL_REQUIRED", status="APPROVED")
    order = _make_order()
    link = _make_link()
    db = _make_db(negotiation=neg, order=order, link=link)

    result = get_payment_required_response(db, "NEG-001")

    assert result["status"] == 402
    assert result["payment_required"] is True
    assert result["order_id"] == "ORD-001"


def test_currency_defaults_to_inr_when_missing():
    neg = _make_negotiation(decision="ALLOWED")
    neg.currency = None  # simulate missing currency
    order = _make_order()
    link = _make_link()
    db = _make_db(negotiation=neg, order=order, link=link)

    result = get_payment_required_response(db, "NEG-001")
    assert result["currency"] == "INR"


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

def test_api_returns_402_status():
    from app.main import app
    from app.database import get_db

    neg = _make_negotiation(decision="ALLOWED")
    order = _make_order()
    link = _make_link()
    db = _make_db(negotiation=neg, order=order, link=link)

    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/x402/payment-required/NEG-001")
    app.dependency_overrides.clear()

    assert response.status_code == 402


def test_api_body_contains_payment_required_true():
    from app.main import app
    from app.database import get_db

    neg = _make_negotiation(decision="ALLOWED")
    order = _make_order()
    link = _make_link()
    db = _make_db(negotiation=neg, order=order, link=link)

    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/x402/payment-required/NEG-001")
    app.dependency_overrides.clear()

    data = response.json()
    assert data["payment_required"] is True
    assert data["payment_provider"] == "razorpay"
    assert data["order_id"] == "ORD-001"
    assert data["payment_link"] == "https://rzp.io/l/test"


def test_api_404_propagates():
    from app.main import app
    from app.database import get_db

    db = _make_db(negotiation=None)
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/x402/payment-required/MISSING")
    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_api_400_propagates_for_rejected():
    from app.main import app
    from app.database import get_db

    neg = _make_negotiation(decision="REJECTED")
    db = _make_db(negotiation=neg)
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/x402/payment-required/NEG-001")
    app.dependency_overrides.clear()

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# BuyerAgent.initiate_payment with x402_response
# ---------------------------------------------------------------------------

def test_buyer_agent_uses_x402_response():
    from app.agents.buyer_agent import BuyerAgent

    buyer = SimpleNamespace(
        buyer_id="BUYER-001",
        budget=100000.0,
        max_single_transaction=50000.0,
        negotiation_strategy="balanced",
    )
    agent = BuyerAgent(buyer)

    neg = _make_negotiation()
    db = _make_db(negotiation=neg)

    x402 = {
        "status": 402,
        "payment_required": True,
        "payment_provider": "razorpay",
        "payment_link": "https://rzp.io/l/test",
        "payment_link_id": "LINK-001",
        "amount": 9000.0,
        "currency": "INR",
        "order_id": "ORD-001",
        "negotiation_id": "NEG-001",
    }

    result = agent.initiate_payment("NEG-001", db, x402_response=x402)

    assert result["order_id"] == "ORD-001"
    assert result["short_url"] == "https://rzp.io/l/test"
    assert result["source"] == "x402"


def test_buyer_agent_falls_back_without_x402():
    from app.agents.buyer_agent import BuyerAgent

    buyer = SimpleNamespace(
        buyer_id="BUYER-001",
        budget=100000.0,
        max_single_transaction=50000.0,
        negotiation_strategy="balanced",
    )
    agent = BuyerAgent(buyer)

    neg = _make_negotiation()
    db = _make_db(negotiation=neg)

    mock_payment = {
        "order_id": "ORD-002",
        "payment_link": "LINK-002",
        "short_url": "https://rzp.io/l/fallback",
        "amount": 9000.0,
        "currency": "INR",
    }

    with patch("app.agents.buyer_agent.create_order_and_link", return_value=mock_payment):
        result = agent.initiate_payment("NEG-001", db)

    assert result["order_id"] == "ORD-002"
    assert "source" not in result


def test_buyer_agent_x402_budget_check_still_enforced():
    from app.agents.buyer_agent import BuyerAgent

    buyer = SimpleNamespace(
        buyer_id="BUYER-001",
        budget=100.0,           # very low budget
        max_single_transaction=100.0,
        negotiation_strategy="balanced",
    )
    agent = BuyerAgent(buyer)

    neg = _make_negotiation(final_amount=9000.0)  # exceeds budget
    db = _make_db(negotiation=neg)

    x402 = {"order_id": "ORD-001", "payment_link": "https://rzp.io/l/test",
             "payment_link_id": "LINK-001", "amount": 9000.0, "currency": "INR"}

    with pytest.raises(HTTPException) as exc:
        agent.initiate_payment("NEG-001", db, x402_response=x402)
    assert exc.value.status_code == 400
