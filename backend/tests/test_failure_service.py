import pytest
from unittest.mock import MagicMock, patch, call
from types import SimpleNamespace
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.services.failure_service import FailureRecoveryService

svc = FailureRecoveryService()

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_negotiation(negotiation_id="NEG-001"):
    return SimpleNamespace(
        negotiation_id=negotiation_id,
        final_amount=9000.0,
        final_discount=0.10,
        policy_version="1.0",
        buyer_id="BUYER-001",
        currency="INR",
        status="PENDING",
    )


def _make_link(link_id="LINK-001", order_id="ORD-001", status="created"):
    return SimpleNamespace(
        id=1,
        link_id=link_id,
        order_id=order_id,
        negotiation_id="NEG-001",
        short_url="https://rzp.io/l/test",
        status=status,
    )


def _make_order(order_id="ORD-001"):
    return SimpleNamespace(
        id=1,
        order_id=order_id,
        negotiation_id="NEG-001",
        amount=9000.0,
        currency="INR",
        receipt="rcpt_NEG-001",
        status="created",
        metadata_json={},
    )


def _make_db(negotiation=None, link=None, order=None):
    db = MagicMock()

    def query_side(model):
        from app.models.negotiation import Negotiation
        from app.models.payment_link import PaymentLink
        from app.models.order import Order
        from app.models.audit import AuditEvent

        q = MagicMock()
        filter_mock = MagicMock()
        order_by_mock = MagicMock()

        if model is Negotiation:
            filter_mock.first.return_value = negotiation
            q.filter.return_value = filter_mock
        elif model is PaymentLink:
            order_by_mock.first.return_value = link
            filter_mock.order_by.return_value = order_by_mock
            q.filter.return_value = filter_mock
        elif model is Order:
            filter_mock.first.return_value = order
            q.filter.return_value = filter_mock
        elif model is AuditEvent:
            order_by_mock.first.return_value = None
            q.order_by.return_value = order_by_mock
        return q

    db.query.side_effect = query_side
    db.refresh.side_effect = lambda obj: None
    return db


# ---------------------------------------------------------------------------
# simulate_expired_payment_link tests
# ---------------------------------------------------------------------------

RZP_ORDER = {"id": "rzp_order_new", "status": "created"}
RZP_LINK = {"id": "rzp_link_new", "status": "created", "short_url": "https://rzp.io/l/new"}


def test_expired_link_not_found_negotiation():
    db = _make_db(negotiation=None)
    with pytest.raises(HTTPException) as exc:
        svc.simulate_expired_payment_link(db, "MISSING")
    assert exc.value.status_code == 404
    assert "Negotiation" in exc.value.detail


def test_expired_link_no_active_link():
    db = _make_db(negotiation=_make_negotiation(), link=None)
    with pytest.raises(HTTPException) as exc:
        svc.simulate_expired_payment_link(db, "NEG-001")
    assert exc.value.status_code == 404
    assert "payment link" in exc.value.detail.lower()


def test_expired_link_marks_old_link_expired():
    link = _make_link()
    order = _make_order()
    db = _make_db(negotiation=_make_negotiation(), link=link, order=order)

    mock_client = MagicMock()
    mock_client.order.cancel.return_value = {}
    mock_client.order.create.return_value = RZP_ORDER
    mock_client.payment_link.create.return_value = RZP_LINK

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            result = svc.simulate_expired_payment_link(db, "NEG-001")

    assert link.status == "expired"
    db.commit.assert_called()


def test_expired_link_cancels_razorpay_order():
    link = _make_link()
    order = _make_order()
    db = _make_db(negotiation=_make_negotiation(), link=link, order=order)

    mock_client = MagicMock()
    mock_client.order.cancel.return_value = {}
    mock_client.order.create.return_value = RZP_ORDER
    mock_client.payment_link.create.return_value = RZP_LINK

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            svc.simulate_expired_payment_link(db, "NEG-001")

    mock_client.order.cancel.assert_called_once_with("ORD-001")


def test_expired_link_creates_new_order_and_link():
    link = _make_link()
    order = _make_order()
    db = _make_db(negotiation=_make_negotiation(), link=link, order=order)

    mock_client = MagicMock()
    mock_client.order.cancel.return_value = {}
    mock_client.order.create.return_value = RZP_ORDER
    mock_client.payment_link.create.return_value = RZP_LINK

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            result = svc.simulate_expired_payment_link(db, "NEG-001")

    assert result["order_id"] == "rzp_order_new"
    assert result["payment_link"] == "rzp_link_new"
    assert result["short_url"] == "https://rzp.io/l/new"
    assert result["message"] == "Payment link renewed successfully"
    assert result["expired_link_id"] == "LINK-001"
    assert "renewed" in result["idempotency_key"]


def test_expired_link_new_idempotency_key_differs():
    link = _make_link()
    order = _make_order()
    db = _make_db(negotiation=_make_negotiation(), link=link, order=order)

    mock_client = MagicMock()
    mock_client.order.cancel.return_value = {}
    mock_client.order.create.return_value = RZP_ORDER
    mock_client.payment_link.create.return_value = RZP_LINK

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            result = svc.simulate_expired_payment_link(db, "NEG-001")

    assert result["idempotency_key"].startswith("NEG-001-renewed-")


def test_expired_link_cancel_failure_is_non_fatal():
    """If Razorpay cancel raises, recovery should still proceed."""
    link = _make_link()
    order = _make_order()
    db = _make_db(negotiation=_make_negotiation(), link=link, order=order)

    mock_client = MagicMock()
    mock_client.order.cancel.side_effect = Exception("cancel failed")
    mock_client.order.create.return_value = RZP_ORDER
    mock_client.payment_link.create.return_value = RZP_LINK

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            result = svc.simulate_expired_payment_link(db, "NEG-001")

    assert result["order_id"] == "rzp_order_new"


def test_expired_link_logs_audit_event():
    link = _make_link()
    order = _make_order()
    db = _make_db(negotiation=_make_negotiation(), link=link, order=order)

    mock_client = MagicMock()
    mock_client.order.cancel.return_value = {}
    mock_client.order.create.return_value = RZP_ORDER
    mock_client.payment_link.create.return_value = RZP_LINK

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event") as mock_audit:
            svc.simulate_expired_payment_link(db, "NEG-001")

    mock_audit.assert_called_once()
    # action_type is passed as a keyword argument
    assert mock_audit.call_args.kwargs["action_type"] == "PAYMENT_LINK_RENEWED"


# ---------------------------------------------------------------------------
# simulate_razorpay_timeout tests
# ---------------------------------------------------------------------------

def test_timeout_negotiation_not_found():
    db = _make_db(negotiation=None)
    with pytest.raises(HTTPException) as exc:
        svc.simulate_razorpay_timeout(db, "MISSING")
    assert exc.value.status_code == 404


def test_timeout_succeeds_on_first_attempt():
    db = _make_db(negotiation=_make_negotiation())
    mock_client = MagicMock()
    mock_client.order.all.return_value = {"items": []}

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            result = svc.simulate_razorpay_timeout(db, "NEG-001")

    assert result["status"] == "recovered"
    assert result["attempts"] == 1


def test_timeout_succeeds_on_last_allowed_attempt():
    """Client fails on attempts 1 and 2, succeeds on attempt 3 (limit=2 → max attempts=3)."""
    db = _make_db(negotiation=_make_negotiation())
    mock_client = MagicMock()
    mock_client.order.all.side_effect = [
        TimeoutError("timeout"),
        TimeoutError("timeout"),
        {"items": []},  # succeeds on 3rd attempt
    ]

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            with patch("app.config.settings.PAYMENT_RETRY_LIMIT", 2):
                result = svc.simulate_razorpay_timeout(db, "NEG-001")

    assert result["status"] == "recovered"
    assert result["attempts"] == 3


def test_timeout_exceeds_retry_limit_raises_502():
    """All attempts fail → 502 raised."""
    db = _make_db(negotiation=_make_negotiation())
    mock_client = MagicMock()
    mock_client.order.all.side_effect = TimeoutError("always fails")

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            with patch("app.config.settings.PAYMENT_RETRY_LIMIT", 2):
                with pytest.raises(HTTPException) as exc:
                    svc.simulate_razorpay_timeout(db, "NEG-001")

    assert exc.value.status_code == 502
    assert "timeout" in exc.value.detail.lower()


def test_timeout_failure_logs_audit_event():
    db = _make_db(negotiation=_make_negotiation())
    mock_client = MagicMock()
    mock_client.order.all.side_effect = TimeoutError("always fails")

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event") as mock_audit:
            with patch("app.config.settings.PAYMENT_RETRY_LIMIT", 2):
                with pytest.raises(HTTPException):
                    svc.simulate_razorpay_timeout(db, "NEG-001")

    mock_audit.assert_called_once()
    assert mock_audit.call_args.kwargs["action_type"] == "PAYMENT_TIMEOUT_FAILED"


def test_timeout_recovery_logs_audit_event():
    db = _make_db(negotiation=_make_negotiation())
    mock_client = MagicMock()
    mock_client.order.all.return_value = {"items": []}

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event") as mock_audit:
            svc.simulate_razorpay_timeout(db, "NEG-001")

    mock_audit.assert_called_once()
    assert mock_audit.call_args.kwargs["action_type"] == "PAYMENT_TIMEOUT_RECOVERED"


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

def test_api_expired_link_endpoint():
    from app.main import app
    from app.database import get_db

    db = _make_db(negotiation=_make_negotiation(), link=_make_link(), order=_make_order())
    mock_client = MagicMock()
    mock_client.order.cancel.return_value = {}
    mock_client.order.create.return_value = RZP_ORDER
    mock_client.payment_link.create.return_value = RZP_LINK

    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            response = client.post(
                "/api/v1/simulate/failures/expired-link",
                json={"negotiation_id": "NEG-001"},
            )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "rzp_order_new"
    assert data["message"] == "Payment link renewed successfully"


def test_api_timeout_endpoint_success():
    from app.main import app
    from app.database import get_db

    db = _make_db(negotiation=_make_negotiation())
    mock_client = MagicMock()
    mock_client.order.all.return_value = {"items": []}

    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            response = client.post(
                "/api/v1/simulate/failures/timeout",
                json={"negotiation_id": "NEG-001"},
            )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "recovered"


def test_api_timeout_endpoint_502():
    from app.main import app
    from app.database import get_db

    db = _make_db(negotiation=_make_negotiation())
    mock_client = MagicMock()
    mock_client.order.all.side_effect = TimeoutError("always fails")

    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)

    with patch("app.services.failure_service.get_razorpay_client", return_value=mock_client):
        with patch("app.services.failure_service.append_audit_event"):
            with patch("app.config.settings.PAYMENT_RETRY_LIMIT", 2):
                response = client.post(
                    "/api/v1/simulate/failures/timeout",
                    json={"negotiation_id": "NEG-001"},
                )

    app.dependency_overrides.clear()
    assert response.status_code == 502
