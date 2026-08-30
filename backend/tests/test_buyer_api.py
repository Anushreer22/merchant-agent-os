import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.services.auth_service import get_current_user

_MOCK_USER = SimpleNamespace(id=1, email="buyer@test.com", full_name="Test",
                              role="buyer", merchant_id=None)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_buyer(**kwargs):
    defaults = dict(
        buyer_id="BUYER_TEST_001",
        name="Test Buyer",
        budget=10000.0,
        currency="INR",
        max_single_transaction=10000.0,
        preferred_categories=["subscriptions"],
        negotiation_strategy="balanced",
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_product():
    return SimpleNamespace(
        product_id="SUB_PRO_001",
        base_price=1000.0,
        currency="INR",
        inventory=50,
        margin_floor=0.30,
        discount_rules={},
    )


def make_negotiation_row(negotiation_id="neg-001", final_amount=900.0):
    return SimpleNamespace(
        negotiation_id=negotiation_id,
        final_amount=final_amount,
        buyer_id="BUYER_TEST_001",
        policy_version="1.0",
        final_discount=0.10,
        currency="INR",
    )


NEG_ALLOWED = {
    "negotiation_id": "neg-001",
    "decision": "ALLOWED",
    "requires_human_approval": False,
    "maximum_allowed_discount": 0.15,
    "counter_offer": None,
    "policy_version": "1.0",
    "reason_code": "WITHIN_POLICY",
    "final_price": 900.0,
    "currency": "INR",
    "created_at": datetime.now(timezone.utc),
}

NEG_REJECTED = {
    **NEG_ALLOWED,
    "decision": "REJECTED",
    "reason_code": "DISCOUNT_EXCEEDS_LIMIT",
    "counter_offer": {"discount": 0.15, "final_unit_price": 850.0},
}

NEG_APPROVAL_REQUIRED = {
    **NEG_ALLOWED,
    "decision": "APPROVAL_REQUIRED",
    "requires_human_approval": True,
    "reason_code": "APPROVAL_REQUIRED",
    "counter_offer": {"discount": 0.15, "final_unit_price": 850.0},
}

PAYMENT_RESULT = {
    "order_id": "order_rzp_001",
    "payment_link": "plink_001",
    "short_url": "https://rzp.io/l/test",
    "amount": 900.0,
    "currency": "INR",
}


def _make_mock_db(buyer=None, product=None, neg_row=None):
    db = MagicMock()

    def query_side_effect(model):
        from app.models.buyer import Buyer
        from app.models.product import Product
        from app.models.negotiation import Negotiation

        q = MagicMock()
        if model is Buyer:
            q.filter.return_value.first.return_value = buyer
        elif model is Product:
            q.filter.return_value.first.return_value = product
        elif model is Negotiation:
            q.filter.return_value.first.return_value = neg_row
        return q

    db.query.side_effect = query_side_effect
    return db


def _override_db(db):
    """Return a FastAPI dependency override that yields the given mock db."""
    def _get_mock_db():
        yield db
    return _get_mock_db


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_purchase_allowed_initiates_payment():
    db = _make_mock_db(buyer=make_buyer(), product=make_product(), neg_row=make_negotiation_row())
    app.dependency_overrides[get_db] = _override_db(db)
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER
    try:
        with patch("app.api.buyers.create_negotiation", return_value=NEG_ALLOWED):
            with patch("app.api.buyers.create_order_and_link", return_value=PAYMENT_RESULT):
                resp = TestClient(app).post(
                    "/api/v1/buyers/BUYER_TEST_001/purchase",
                    json={"product_id": "SUB_PRO_001", "quantity": 1, "desired_discount": 0.10},
                )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "payment_initiated"
    assert data["payment"]["order_id"] == "order_rzp_001"


def test_purchase_rejected_returns_counter_offer():
    db = _make_mock_db(buyer=make_buyer(), product=make_product())
    app.dependency_overrides[get_db] = _override_db(db)
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER
    try:
        with patch("app.api.buyers.create_negotiation", return_value=NEG_REJECTED):
            resp = TestClient(app).post(
                "/api/v1/buyers/BUYER_TEST_001/purchase",
                json={"product_id": "SUB_PRO_001", "quantity": 1, "desired_discount": 0.30},
            )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"
    assert data["counter_offer"] is not None


def test_purchase_budget_exceeded():
    db = _make_mock_db(buyer=make_buyer(budget=100, max_single_transaction=100), product=make_product())
    app.dependency_overrides[get_db] = _override_db(db)
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER
    try:
        with patch("app.api.buyers.create_negotiation", return_value=NEG_ALLOWED):
            resp = TestClient(app).post(
                "/api/v1/buyers/BUYER_TEST_001/purchase",
                json={"product_id": "SUB_PRO_001", "quantity": 1, "desired_discount": 0.10},
            )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "budget_exceeded"
    assert "budget" in data["message"].lower()


def test_purchase_approval_required():
    db = _make_mock_db(buyer=make_buyer(), product=make_product())
    app.dependency_overrides[get_db] = _override_db(db)
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER
    try:
        with patch("app.api.buyers.create_negotiation", return_value=NEG_APPROVAL_REQUIRED):
            resp = TestClient(app).post(
                "/api/v1/buyers/BUYER_TEST_001/purchase",
                json={"product_id": "SUB_PRO_001", "quantity": 1, "desired_discount": 0.18},
            )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "approval_required"
    assert data["negotiation_id"] == "neg-001"


def test_purchase_buyer_not_found():
    db = _make_mock_db(buyer=None)
    app.dependency_overrides[get_db] = _override_db(db)
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER
    try:
        resp = TestClient(app).post(
            "/api/v1/buyers/NONEXISTENT/purchase",
            json={"product_id": "SUB_PRO_001", "quantity": 1, "desired_discount": 0.10},
        )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 404


def test_purchase_product_not_found():
    db = _make_mock_db(buyer=make_buyer(), product=None)
    app.dependency_overrides[get_db] = _override_db(db)
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER
    try:
        resp = TestClient(app).post(
            "/api/v1/buyers/BUYER_TEST_001/purchase",
            json={"product_id": "MISSING", "quantity": 1, "desired_discount": 0.10},
        )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 404
