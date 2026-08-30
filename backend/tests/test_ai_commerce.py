import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from datetime import datetime, timezone
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.services.ai_commerce_service import AICommerceOrchestrator


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def make_buyer(**kwargs):
    defaults = dict(
        buyer_id="BUYER_001",
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


def make_negotiation_row(negotiation_id="neg-001", final_amount=900.0):
    return SimpleNamespace(
        negotiation_id=negotiation_id,
        final_amount=final_amount,
        buyer_id="BUYER_001",
        policy_version="1.0",
        final_discount=0.10,
        currency="INR",
    )


def make_approval(approval_id="APR-test-001"):
    return SimpleNamespace(
        approval_id=approval_id,
        negotiation_id="neg-001",
        status="PENDING",
        created_at=datetime.now(timezone.utc),
    )


# create_negotiation return shapes
def _neg_allowed(negotiation_id="neg-001", final_price=900.0):
    return {
        "decision": "ALLOWED",
        "requires_human_approval": False,
        "maximum_allowed_discount": 0.15,
        "counter_offer": None,
        "policy_version": "1.0",
        "reason_code": "WITHIN_POLICY",
        "negotiation_id": negotiation_id,
        "final_price": final_price,
        "currency": "INR",
    }


def _neg_approval_required(negotiation_id="neg-002"):
    return {
        "decision": "APPROVAL_REQUIRED",
        "requires_human_approval": True,
        "maximum_allowed_discount": 0.15,
        "counter_offer": {"discount": 0.15, "final_unit_price": 850.0},
        "policy_version": "1.0",
        "reason_code": "APPROVAL_REQUIRED",
        "negotiation_id": negotiation_id,
        "final_price": 820.0,
        "currency": "INR",
    }


def _neg_rejected(negotiation_id="neg-003"):
    return {
        "decision": "REJECTED",
        "requires_human_approval": False,
        "maximum_allowed_discount": 0.15,
        "counter_offer": {"discount": 0.15, "final_unit_price": 850.0},
        "policy_version": "1.0",
        "reason_code": "DISCOUNT_EXCEEDS_LIMIT",
        "negotiation_id": negotiation_id,
        "final_price": 850.0,
        "currency": "INR",
    }


PAYMENT_RESULT = {
    "order_id": "order_rzp_001",
    "payment_link": "plink_001",
    "short_url": "https://rzp.io/l/test",
    "amount": 900.0,
    "currency": "INR",
}


def _make_db(buyer=None, product=None, neg_row=None):
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

    def refresh_side_effect(obj):
        if not hasattr(obj, "created_at") or obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)

    db.refresh.side_effect = refresh_side_effect
    return db


# ---------------------------------------------------------------------------
# Unit tests for AICommerceOrchestrator
# ---------------------------------------------------------------------------

orchestrator = AICommerceOrchestrator()


def test_full_flow_allowed_payment_pending():
    db = _make_db(
        buyer=make_buyer(),
        product=make_product(),
        neg_row=make_negotiation_row(final_amount=900.0),
    )
    with patch("app.services.ai_commerce_service.create_negotiation",
               return_value=_neg_allowed()):
        with patch("app.services.ai_commerce_service.BuyerAgent.initiate_payment",
                   return_value=PAYMENT_RESULT):
            result = orchestrator.run_transaction(db, "BUYER_001", "SUB_PRO_001", 1, 0.10)

    assert result["status"] == "payment_pending"
    assert result["negotiation_id"] == "neg-001"
    assert result["payment"]["order_id"] == "order_rzp_001"
    assert result["payment"]["short_url"] == "https://rzp.io/l/test"
    # Transcript should have 4 steps: make_offer, evaluate_offer, budget_check, initiate_payment
    assert len(result["transcript"]) == 4
    assert result["transcript"][0]["actor"] == "buyer_agent"
    assert result["transcript"][1]["actor"] == "merchant_agent"
    assert result["transcript"][2]["detail"]["passed"] is True
    assert result["transcript"][3]["action"] == "initiate_payment"


def test_flow_approval_required_no_payment():
    approval = make_approval()
    db = _make_db(buyer=make_buyer(), product=make_product())
    with patch("app.services.ai_commerce_service.create_negotiation",
               return_value=_neg_approval_required()):
        with patch("app.services.ai_commerce_service.create_approval",
                   return_value=approval):
            result = orchestrator.run_transaction(db, "BUYER_001", "SUB_PRO_001", 1, 0.18)

    assert result["status"] == "approval_required"
    assert result["approval_id"] == "APR-test-001"
    assert result["negotiation_id"] == "neg-002"
    assert "payment" not in result
    # Transcript: make_offer, evaluate_offer, create_approval
    assert len(result["transcript"]) == 3
    assert result["transcript"][2]["action"] == "create_approval"


def test_flow_rejected_returns_counter_offer():
    db = _make_db(buyer=make_buyer(), product=make_product())
    with patch("app.services.ai_commerce_service.create_negotiation",
               return_value=_neg_rejected()):
        result = orchestrator.run_transaction(db, "BUYER_001", "SUB_PRO_001", 1, 0.30)

    assert result["status"] == "rejected"
    assert result["counter_offer"] is not None
    assert result["counter_offer"]["discount"] == pytest.approx(0.15)
    assert "payment" not in result
    assert result["transcript"][2]["action"] == "terminate"


def test_flow_budget_exceeded():
    # Buyer has tiny budget — final_price=900 > budget=100
    db = _make_db(
        buyer=make_buyer(budget=100, max_single_transaction=100),
        product=make_product(),
        neg_row=make_negotiation_row(final_amount=900.0),
    )
    with patch("app.services.ai_commerce_service.create_negotiation",
               return_value=_neg_allowed(final_price=900.0)):
        result = orchestrator.run_transaction(db, "BUYER_001", "SUB_PRO_001", 1, 0.10)

    assert result["status"] == "budget_exceeded"
    assert result["negotiation_id"] == "neg-001"
    assert "payment" not in result
    assert result["transcript"][2]["detail"]["passed"] is False


def test_flow_buyer_not_found_raises_404():
    db = _make_db(buyer=None)
    with pytest.raises(HTTPException) as exc:
        orchestrator.run_transaction(db, "MISSING", "SUB_PRO_001", 1, 0.10)
    assert exc.value.status_code == 404


def test_flow_product_not_found_raises_404():
    db = _make_db(buyer=make_buyer(), product=None)
    with pytest.raises(HTTPException) as exc:
        orchestrator.run_transaction(db, "BUYER_001", "MISSING", 1, 0.10)
    assert exc.value.status_code == 404


def test_transcript_step_actors_and_order():
    db = _make_db(
        buyer=make_buyer(),
        product=make_product(),
        neg_row=make_negotiation_row(),
    )
    with patch("app.services.ai_commerce_service.create_negotiation",
               return_value=_neg_allowed()):
        with patch("app.services.ai_commerce_service.BuyerAgent.initiate_payment",
                   return_value=PAYMENT_RESULT):
            result = orchestrator.run_transaction(db, "BUYER_001", "SUB_PRO_001", 1, 0.10)

    actors = [s["actor"] for s in result["transcript"]]
    assert actors == ["buyer_agent", "merchant_agent", "buyer_agent", "buyer_agent"]


def test_approval_creation_failure_still_returns_approval_required():
    # Even if create_approval raises, orchestrator should return approval_required gracefully
    db = _make_db(buyer=make_buyer(), product=make_product())
    with patch("app.services.ai_commerce_service.create_negotiation",
               return_value=_neg_approval_required()):
        with patch("app.services.ai_commerce_service.create_approval",
                   side_effect=Exception("DB error")):
            result = orchestrator.run_transaction(db, "BUYER_001", "SUB_PRO_001", 1, 0.18)

    assert result["status"] == "approval_required"
    assert result["approval_id"] is None  # gracefully None when creation failed


# ---------------------------------------------------------------------------
# API-level tests via TestClient + dependency_overrides
# ---------------------------------------------------------------------------

def _override_db(db):
    def _get():
        yield db
    return _get


def test_api_simulate_allowed():
    db = _make_db(
        buyer=make_buyer(),
        product=make_product(),
        neg_row=make_negotiation_row(),
    )
    app.dependency_overrides[get_db] = _override_db(db)
    try:
        with patch("app.services.ai_commerce_service.create_negotiation",
                   return_value=_neg_allowed()):
            with patch("app.services.ai_commerce_service.BuyerAgent.initiate_payment",
                       return_value=PAYMENT_RESULT):
                resp = TestClient(app).post(
                    "/api/v1/simulate/ai-commerce",
                    json={"buyer_id": "BUYER_001", "product_id": "SUB_PRO_001",
                          "quantity": 1, "desired_discount": 0.10},
                )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    assert resp.json()["status"] == "payment_pending"


def test_api_simulate_rejected():
    db = _make_db(buyer=make_buyer(), product=make_product())
    app.dependency_overrides[get_db] = _override_db(db)
    try:
        with patch("app.services.ai_commerce_service.create_negotiation",
                   return_value=_neg_rejected()):
            resp = TestClient(app).post(
                "/api/v1/simulate/ai-commerce",
                json={"buyer_id": "BUYER_001", "product_id": "SUB_PRO_001",
                      "quantity": 1, "desired_discount": 0.30},
            )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"


def test_api_simulate_buyer_not_found():
    db = _make_db(buyer=None)
    app.dependency_overrides[get_db] = _override_db(db)
    try:
        resp = TestClient(app).post(
            "/api/v1/simulate/ai-commerce",
            json={"buyer_id": "MISSING", "product_id": "SUB_PRO_001",
                  "quantity": 1, "desired_discount": 0.10},
        )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 404
