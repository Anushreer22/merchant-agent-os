import json
import hmac
import hashlib
import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from datetime import datetime, timezone
from fastapi import HTTPException

from app.payments.webhook_service import verify_webhook_signature, process_webhook_event


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WEBHOOK_SECRET = "test_webhook_secret"

PAYMENT_CAPTURED_PAYLOAD = {
    "id": "evt_001",
    "event": "payment.captured",
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_001",
                "order_id": "order_rzp_001",
                "amount": 180000,
                "currency": "INR",
            }
        }
    },
}

ORDER_PAID_PAYLOAD = {
    "id": "evt_002",
    "event": "order.paid",
    "payload": {
        "order": {
            "entity": {
                "id": "order_rzp_002",
                "amount": 90000,
                "currency": "INR",
            }
        }
    },
}

PAYMENT_FAILED_PAYLOAD = {
    "id": "evt_003",
    "event": "payment.failed",
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_003",
                "order_id": "order_rzp_003",
            }
        }
    },
}


def _sign(payload: dict, secret: str = WEBHOOK_SECRET) -> str:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


def make_order(order_id: str, status: str = "created"):
    return SimpleNamespace(order_id=order_id, status=status)


def make_db(existing_event=None, order=None):
    db = MagicMock()

    def query_side_effect(model):
        from app.models.webhook_event import WebhookEvent
        from app.models.order import Order

        q = MagicMock()
        if model is WebhookEvent:
            q.filter.return_value.first.return_value = existing_event
        elif model is Order:
            q.filter.return_value.first.return_value = order
        return q

    db.query.side_effect = query_side_effect
    return db


# ---------------------------------------------------------------------------
# verify_webhook_signature tests
# ---------------------------------------------------------------------------

def test_valid_signature():
    body = b'{"id":"evt_001"}'
    sig = hmac.new(key=WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256).hexdigest()
    assert verify_webhook_signature(body, sig, WEBHOOK_SECRET) is True


def test_invalid_signature():
    body = b'{"id":"evt_001"}'
    assert verify_webhook_signature(body, "bad_signature", WEBHOOK_SECRET) is False


def test_tampered_body_fails():
    body = b'{"id":"evt_001"}'
    sig = hmac.new(key=WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256).hexdigest()
    assert verify_webhook_signature(b'{"id":"evt_tampered"}', sig, WEBHOOK_SECRET) is False


# ---------------------------------------------------------------------------
# process_webhook_event tests
# ---------------------------------------------------------------------------

def test_invalid_signature_raises_401():
    db = make_db()
    with patch("app.payments.webhook_service.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = WEBHOOK_SECRET
        with pytest.raises(HTTPException) as exc:
            process_webhook_event(db, PAYMENT_CAPTURED_PAYLOAD, "wrong_sig")
    assert exc.value.status_code == 401
    assert "Invalid signature" in exc.value.detail


def test_missing_event_id_raises_400():
    db = make_db()
    bad_payload = {"event": "payment.captured"}  # no "id"
    sig = _sign(bad_payload)
    with patch("app.payments.webhook_service.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = WEBHOOK_SECRET
        with pytest.raises(HTTPException) as exc:
            process_webhook_event(db, bad_payload, sig)
    assert exc.value.status_code == 400


def test_missing_event_type_raises_400():
    db = make_db()
    bad_payload = {"id": "evt_x"}  # no "event"
    sig = _sign(bad_payload)
    with patch("app.payments.webhook_service.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = WEBHOOK_SECRET
        with pytest.raises(HTTPException) as exc:
            process_webhook_event(db, bad_payload, sig)
    assert exc.value.status_code == 400


def test_duplicate_event_returns_duplicate_status():
    existing = SimpleNamespace(event_id="evt_001", processed=True)
    db = make_db(existing_event=existing)
    sig = _sign(PAYMENT_CAPTURED_PAYLOAD)
    with patch("app.payments.webhook_service.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = WEBHOOK_SECRET
        result = process_webhook_event(db, PAYMENT_CAPTURED_PAYLOAD, sig)
    assert result["status"] == "duplicate"
    assert result["event_id"] == "evt_001"
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_payment_captured_updates_order_to_paid():
    order = make_order("order_rzp_001")
    db = make_db(existing_event=None, order=order)
    sig = _sign(PAYMENT_CAPTURED_PAYLOAD)
    with patch("app.payments.webhook_service.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = WEBHOOK_SECRET
        result = process_webhook_event(db, PAYMENT_CAPTURED_PAYLOAD, sig)
    assert result["status"] == "processed"
    assert result["event_id"] == "evt_001"
    assert order.status == "paid"
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_order_paid_updates_order_status():
    order = make_order("order_rzp_002")
    db = make_db(existing_event=None, order=order)
    sig = _sign(ORDER_PAID_PAYLOAD)
    with patch("app.payments.webhook_service.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = WEBHOOK_SECRET
        result = process_webhook_event(db, ORDER_PAID_PAYLOAD, sig)
    assert result["status"] == "processed"
    assert order.status == "paid"


def test_payment_failed_updates_order_to_failed():
    order = make_order("order_rzp_003")
    db = make_db(existing_event=None, order=order)
    sig = _sign(PAYMENT_FAILED_PAYLOAD)
    with patch("app.payments.webhook_service.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = WEBHOOK_SECRET
        result = process_webhook_event(db, PAYMENT_FAILED_PAYLOAD, sig)
    assert result["status"] == "processed"
    assert order.status == "failed"


def test_unknown_event_type_still_stored():
    db = make_db(existing_event=None, order=None)
    unknown_payload = {"id": "evt_unknown", "event": "refund.created", "payload": {}}
    sig = _sign(unknown_payload)
    with patch("app.payments.webhook_service.settings") as mock_settings:
        mock_settings.RAZORPAY_WEBHOOK_SECRET = WEBHOOK_SECRET
        result = process_webhook_event(db, unknown_payload, sig)
    assert result["status"] == "processed"
    # WebhookEvent row should still be added
    db.add.assert_called_once()
    db.commit.assert_called_once()
