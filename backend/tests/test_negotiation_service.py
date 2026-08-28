import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from datetime import datetime, timezone
from fastapi import HTTPException

from app.services.negotiation_service import create_negotiation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RULES = {
    "max_auto_discount": 0.15,
    "max_human_approved_discount": 0.20,
    "margin_floor": 0.30,
    "human_approval_amount": 5000,
    "max_quantity_without_approval": 20,
    "max_retry_count": 2,
}

POLICY = SimpleNamespace(version="1.0", rules=RULES)


def make_product(**kwargs):
    defaults = dict(
        product_id="PROD_001",
        base_price=1000,
        currency="INR",
        inventory=50,
        margin_floor=0.30,
        discount_rules={},
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_db(product=None, policy=POLICY, existing_neg=None):
    """Return a mock DB session wired to return given product/policy/negotiation."""
    db = MagicMock()

    def query_side_effect(model):
        from app.models.product import Product
        from app.models.negotiation import Negotiation

        q = MagicMock()
        if model is Product:
            q.filter.return_value.first.return_value = product
        elif model is Negotiation:
            filter_mock = MagicMock()
            filter_mock.first.return_value = existing_neg
            q.filter.return_value = filter_mock
        return q

    db.query.side_effect = query_side_effect

    def refresh_side_effect(obj):
        if not hasattr(obj, "created_at") or obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)

    db.refresh.side_effect = refresh_side_effect
    return db


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_product_not_found():
    db = make_db(product=None)
    with patch("app.services.negotiation_service.get_active_policy", return_value=POLICY):
        with pytest.raises(HTTPException) as exc:
            create_negotiation(db, "buyer1", "MISSING", 1, 0.10)
    assert exc.value.status_code == 404


def test_no_active_policy():
    db = make_db(product=make_product())
    with patch("app.services.negotiation_service.get_active_policy", return_value=None):
        with pytest.raises(HTTPException) as exc:
            create_negotiation(db, "buyer1", "PROD_001", 1, 0.10)
    assert exc.value.status_code == 500


def test_discount_allowed():
    # base_price=1000, discount=0.10 -> total=900 < 5000 threshold -> ALLOWED
    product = make_product(base_price=1000)
    db = make_db(product=product)
    with patch("app.services.negotiation_service.get_active_policy", return_value=POLICY):
        result = create_negotiation(db, "buyer1", "PROD_001", 1, 0.10)
    assert result["decision"] == "ALLOWED"
    assert result["requires_human_approval"] is False
    assert result["reason_code"] == "WITHIN_POLICY"
    assert result["final_price"] == pytest.approx(900.0)
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_discount_approval_required():
    # discount=0.18 > max_auto=0.15 -> APPROVAL_REQUIRED
    product = make_product(base_price=1000)
    db = make_db(product=product)
    with patch("app.services.negotiation_service.get_active_policy", return_value=POLICY):
        result = create_negotiation(db, "buyer1", "PROD_001", 1, 0.18)
    assert result["decision"] == "APPROVAL_REQUIRED"
    assert result["requires_human_approval"] is True
    assert result["reason_code"] == "APPROVAL_REQUIRED"


def test_discount_rejected_exceeds_human_limit():
    # discount=0.30 > max_human_approved=0.20 -> REJECTED
    product = make_product(base_price=1000)
    db = make_db(product=product)
    with patch("app.services.negotiation_service.get_active_policy", return_value=POLICY):
        result = create_negotiation(db, "buyer1", "PROD_001", 1, 0.30)
    assert result["decision"] == "REJECTED"
    assert result["reason_code"] == "DISCOUNT_EXCEEDS_LIMIT"
    assert result["counter_offer"] is not None


def test_idempotency_returns_existing():
    product = make_product(base_price=1000)
    existing = SimpleNamespace(
        negotiation_id="existing-uuid",
        product_id="PROD_001",
        buyer_id="buyer1",
        quantity=1,
        requested_discount=0.10,
        final_discount=0.10,
        final_amount=900.0,
        decision="ALLOWED",
        requires_human_approval=False,
        policy_version="1.0",
        reason_code="WITHIN_POLICY",
        status="PENDING",
        idempotency_key="key-abc",
        created_at=datetime.now(timezone.utc),
    )
    db = make_db(product=product, existing_neg=existing)
    with patch("app.services.negotiation_service.get_active_policy", return_value=POLICY):
        result = create_negotiation(db, "buyer1", "PROD_001", 1, 0.10, idempotency_key="key-abc")
    assert result["negotiation_id"] == "existing-uuid"
    # Should NOT have added a new row
    db.add.assert_not_called()


def test_idempotency_no_duplicate_commit():
    product = make_product(base_price=1000)
    existing = SimpleNamespace(
        negotiation_id="existing-uuid-2",
        product_id="PROD_001",
        buyer_id="buyer1",
        quantity=2,
        requested_discount=0.18,
        final_discount=0.15,
        final_amount=1700.0,
        decision="APPROVAL_REQUIRED",
        requires_human_approval=True,
        policy_version="1.0",
        reason_code="APPROVAL_REQUIRED",
        status="PENDING",
        idempotency_key="key-xyz",
        created_at=datetime.now(timezone.utc),
    )
    db = make_db(product=product, existing_neg=existing)
    with patch("app.services.negotiation_service.get_active_policy", return_value=POLICY):
        result = create_negotiation(db, "buyer1", "PROD_001", 2, 0.18, idempotency_key="key-xyz")
    assert result["negotiation_id"] == "existing-uuid-2"
    assert result["decision"] == "APPROVAL_REQUIRED"
    db.commit.assert_not_called()
