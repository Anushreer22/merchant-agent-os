import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from datetime import datetime, timezone
from fastapi import HTTPException

from app.payments.payment_service import create_order_and_link


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_negotiation(**kwargs):
    defaults = dict(
        negotiation_id="neg-uuid-001",
        buyer_id="buyer1",
        product_id="PROD_001",
        quantity=2,
        requested_discount=0.10,
        final_discount=0.10,
        final_amount=1800.0,
        decision="ALLOWED",
        requires_human_approval=False,
        policy_version="1.0",
        reason_code="WITHIN_POLICY",
        status="PENDING",
        currency="INR",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


RZP_ORDER = {"id": "order_rzp_001", "status": "created", "amount": 180000, "currency": "INR"}
RZP_LINK = {"id": "plink_rzp_001", "short_url": "https://rzp.io/l/test", "status": "created"}


def make_mock_client(order_response=RZP_ORDER, link_response=RZP_LINK,
                     order_raises=None, link_raises=None):
    client = MagicMock()
    if order_raises:
        client.order.create.side_effect = order_raises
    else:
        client.order.create.return_value = order_response
    if link_raises:
        client.payment_link.create.side_effect = link_raises
    else:
        client.payment_link.create.return_value = link_response
    return client


def make_db(existing_order=None, existing_link=None):
    db = MagicMock()

    def query_side_effect(model):
        from app.models.order import Order
        from app.models.payment_link import PaymentLink

        q = MagicMock()
        if model is Order:
            q.filter.return_value.first.return_value = existing_order
        elif model is PaymentLink:
            q.filter.return_value.first.return_value = existing_link
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

def test_create_order_and_link_success():
    negotiation = make_negotiation()
    db = make_db()
    mock_client = make_mock_client()

    with patch("app.payments.payment_service.get_razorpay_client", return_value=mock_client):
        result = create_order_and_link(db, negotiation)

    assert result["order_id"] == "order_rzp_001"
    assert result["payment_link"] == "plink_rzp_001"
    assert result["short_url"] == "https://rzp.io/l/test"
    assert result["amount"] == pytest.approx(1800.0)
    assert result["currency"] == "INR"

    # Verify Razorpay was called with correct paise amount
    mock_client.order.create.assert_called_once()
    call_args = mock_client.order.create.call_args[0][0]
    assert call_args["amount"] == 180000  # 1800 * 100
    assert call_args["currency"] == "INR"
    assert call_args["receipt"] == "rcpt_neg-uuid-001"

    # Verify DB rows were persisted
    assert db.add.call_count == 2
    db.commit.assert_called_once()


def test_idempotency_returns_existing_order():
    negotiation = make_negotiation()
    existing_order = SimpleNamespace(
        order_id="order_rzp_existing",
        negotiation_id="neg-uuid-001",
        amount=1800.0,
        currency="INR",
        receipt="rcpt_neg-uuid-001",
        status="created",
    )
    existing_link = SimpleNamespace(
        link_id="plink_existing",
        short_url="https://rzp.io/l/existing",
        status="created",
    )
    db = make_db(existing_order=existing_order, existing_link=existing_link)
    mock_client = make_mock_client()

    with patch("app.payments.payment_service.get_razorpay_client", return_value=mock_client):
        result = create_order_and_link(db, negotiation)

    assert result["order_id"] == "order_rzp_existing"
    assert result["payment_link"] == "plink_existing"
    assert result["short_url"] == "https://rzp.io/l/existing"

    # Razorpay should NOT have been called
    mock_client.order.create.assert_not_called()
    mock_client.payment_link.create.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_razorpay_order_error_raises_502():
    negotiation = make_negotiation()
    db = make_db()
    mock_client = make_mock_client(order_raises=Exception("Razorpay unavailable"))

    with patch("app.payments.payment_service.get_razorpay_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            create_order_and_link(db, negotiation)

    assert exc.value.status_code == 502
    assert "Payment provider error" in exc.value.detail


def test_razorpay_link_error_raises_502():
    negotiation = make_negotiation()
    db = make_db()
    mock_client = make_mock_client(link_raises=Exception("Link service down"))

    with patch("app.payments.payment_service.get_razorpay_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            create_order_and_link(db, negotiation)

    assert exc.value.status_code == 502
    assert "Payment provider error" in exc.value.detail


def test_metadata_contains_required_fields():
    negotiation = make_negotiation()
    db = make_db()
    mock_client = make_mock_client()

    with patch("app.payments.payment_service.get_razorpay_client", return_value=mock_client):
        create_order_and_link(db, negotiation)

    notes = mock_client.order.create.call_args[0][0]["notes"]
    assert notes["negotiation_id"] == "neg-uuid-001"
    assert notes["buyer_id"] == "buyer1"
    assert notes["merchant_id"] == "MERCHANT_001"
    assert notes["discount_applied"] == pytest.approx(0.10)
    assert notes["policy_version"] == "1.0"


def test_amount_conversion_to_paise():
    # Verify fractional rupee amounts are correctly rounded to paise
    negotiation = make_negotiation(final_amount=999.99)
    db = make_db()
    mock_client = make_mock_client()

    with patch("app.payments.payment_service.get_razorpay_client", return_value=mock_client):
        create_order_and_link(db, negotiation)

    call_args = mock_client.order.create.call_args[0][0]
    assert call_args["amount"] == 99999  # round(999.99 * 100)
