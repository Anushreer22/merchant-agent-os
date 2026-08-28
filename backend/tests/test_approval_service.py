import pytest
from unittest.mock import MagicMock, call
from types import SimpleNamespace
from datetime import datetime, timezone
from fastapi import HTTPException

from app.services.approval_service import create_approval, decide_approval, get_approval


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_negotiation(**kwargs):
    defaults = dict(
        negotiation_id="neg-001",
        buyer_id="buyer1",
        product_id="PROD_001",
        quantity=2,
        requested_discount=0.18,
        final_discount=0.15,
        final_amount=1700.0,
        decision="APPROVAL_REQUIRED",
        requires_human_approval=True,
        policy_version="1.0",
        reason_code="APPROVAL_REQUIRED",
        status="PENDING",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_approval(**kwargs):
    defaults = dict(
        approval_id="APR-test-001",
        negotiation_id="neg-001",
        buyer_id="buyer1",
        product_id="PROD_001",
        quantity=2,
        requested_discount=0.18,
        proposed_discount=0.15,
        final_price=1700.0,
        margin_after_discount=0.85,
        policy_version="1.0",
        reason_code="APPROVAL_REQUIRED",
        status="PENDING",
        human_user_id=None,
        approval_reason=None,
        created_at=datetime.now(timezone.utc),
        decided_at=None,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_db(negotiation=None, approval=None):
    db = MagicMock()

    def query_side_effect(model):
        from app.models.negotiation import Negotiation
        from app.models.approval import Approval

        q = MagicMock()
        if model is Negotiation:
            q.filter.return_value.first.return_value = negotiation
        elif model is Approval:
            q.filter.return_value.first.return_value = approval
        return q

    db.query.side_effect = query_side_effect

    def refresh_side_effect(obj):
        if not hasattr(obj, "created_at") or obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)

    db.refresh.side_effect = refresh_side_effect
    return db


# ---------------------------------------------------------------------------
# create_approval tests
# ---------------------------------------------------------------------------

def test_create_approval_success():
    neg = make_negotiation()
    db = make_db(negotiation=neg)
    result = create_approval(db, "neg-001")

    assert result.negotiation_id == "neg-001"
    assert result.status == "PENDING"
    assert float(result.proposed_discount) == pytest.approx(0.15)
    assert float(result.final_price) == pytest.approx(1700.0)
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_create_approval_negotiation_not_found():
    db = make_db(negotiation=None)
    with pytest.raises(HTTPException) as exc:
        create_approval(db, "missing-neg")
    assert exc.value.status_code == 404


def test_create_approval_not_required_raises_400():
    neg = make_negotiation(decision="ALLOWED")
    db = make_db(negotiation=neg)
    with pytest.raises(HTTPException) as exc:
        create_approval(db, "neg-001")
    assert exc.value.status_code == 400
    assert "No approval needed" in exc.value.detail


def test_create_approval_rejected_decision_raises_400():
    neg = make_negotiation(decision="REJECTED")
    db = make_db(negotiation=neg)
    with pytest.raises(HTTPException) as exc:
        create_approval(db, "neg-001")
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# decide_approval tests
# ---------------------------------------------------------------------------

def test_decide_approval_approved_updates_negotiation():
    neg = make_negotiation()
    apr = make_approval()
    db = make_db(negotiation=neg, approval=apr)

    result = decide_approval(db, "APR-test-001", "APPROVED", "manager1", "Looks good")

    assert result.status == "APPROVED"
    assert result.human_user_id == "manager1"
    assert result.approval_reason == "Looks good"
    assert result.decided_at is not None
    assert neg.status == "APPROVED"
    assert neg.final_discount == apr.proposed_discount
    assert neg.final_amount == apr.final_price
    db.commit.assert_called_once()


def test_decide_approval_rejected_updates_negotiation():
    neg = make_negotiation()
    apr = make_approval()
    db = make_db(negotiation=neg, approval=apr)

    result = decide_approval(db, "APR-test-001", "REJECTED", "manager2", "Too high")

    assert result.status == "REJECTED"
    assert neg.status == "REJECTED"
    db.commit.assert_called_once()


def test_decide_approval_not_found_raises_404():
    db = make_db(approval=None)
    with pytest.raises(HTTPException) as exc:
        decide_approval(db, "APR-missing", "APPROVED", "manager1")
    assert exc.value.status_code == 404


def test_decide_approval_already_decided_raises_409():
    apr = make_approval(status="APPROVED")
    db = make_db(approval=apr)
    with pytest.raises(HTTPException) as exc:
        decide_approval(db, "APR-test-001", "APPROVED", "manager1")
    assert exc.value.status_code == 409
    assert "already decided" in exc.value.detail


def test_decide_approval_already_rejected_raises_409():
    apr = make_approval(status="REJECTED")
    db = make_db(approval=apr)
    with pytest.raises(HTTPException) as exc:
        decide_approval(db, "APR-test-001", "REJECTED", "manager1")
    assert exc.value.status_code == 409


def test_decide_approval_no_commit_on_404():
    db = make_db(approval=None)
    with pytest.raises(HTTPException):
        decide_approval(db, "APR-missing", "APPROVED", "manager1")
    db.commit.assert_not_called()


# ---------------------------------------------------------------------------
# get_approval tests
# ---------------------------------------------------------------------------

def test_get_approval_success():
    apr = make_approval()
    db = make_db(approval=apr)
    result = get_approval(db, "APR-test-001")
    assert result.approval_id == "APR-test-001"
    assert result.status == "PENDING"


def test_get_approval_not_found_raises_404():
    db = make_db(approval=None)
    with pytest.raises(HTTPException) as exc:
        get_approval(db, "APR-missing")
    assert exc.value.status_code == 404


def test_get_approval_after_decision():
    apr = make_approval(status="APPROVED", human_user_id="manager1", decided_at=datetime.now(timezone.utc))
    db = make_db(approval=apr)
    result = get_approval(db, "APR-test-001")
    assert result.status == "APPROVED"
    assert result.human_user_id == "manager1"
    assert result.decided_at is not None
