import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from fastapi.testclient import TestClient

from app.audit.hashing import canonicalize_payload, compute_sha256, compute_event_hash
from app.audit.ledger import append_audit_event, validate_audit_chain
from app.models.audit import AuditEvent


# ---------------------------------------------------------------------------
# Hashing unit tests
# ---------------------------------------------------------------------------

def test_canonicalize_payload_sorts_keys():
    result = canonicalize_payload({"z": 1, "a": 2, "m": 3})
    assert result == '{"a":2,"m":3,"z":1}'


def test_canonicalize_payload_nested():
    result = canonicalize_payload({"b": {"y": 1, "x": 2}, "a": 0})
    assert result == '{"a":0,"b":{"x":2,"y":1}}'


def test_compute_sha256_deterministic():
    h1 = compute_sha256("hello")
    h2 = compute_sha256("hello")
    assert h1 == h2
    assert len(h1) == 64


def test_compute_sha256_different_inputs():
    assert compute_sha256("hello") != compute_sha256("world")


def test_compute_event_hash_returns_tuple():
    payload_hash, event_hash = compute_event_hash("GENESIS", {"action": "test"})
    assert len(payload_hash) == 64
    assert len(event_hash) == 64
    assert payload_hash != event_hash


def test_compute_event_hash_chaining():
    ph1, h1 = compute_event_hash("GENESIS", {"a": 1})
    ph2, h2 = compute_event_hash(h1, {"a": 2})
    # Different previous_hash => different event hash
    assert h1 != h2


# ---------------------------------------------------------------------------
# Helpers for ledger tests
# ---------------------------------------------------------------------------

def _make_db_with_events(events: list):
    """Return a mock DB that returns `events` from query().order_by().all()
    and the last event from query().order_by().first()."""
    db = MagicMock()

    def query_side(model):
        q = MagicMock()
        order_mock = MagicMock()
        order_mock.all.return_value = events
        order_mock.first.return_value = events[-1] if events else None
        order_mock.offset.return_value.limit.return_value.all.return_value = events
        q.order_by.return_value = order_mock
        return q

    db.query.side_effect = query_side

    def refresh_side(obj):
        pass

    db.refresh.side_effect = refresh_side
    return db


def _make_event(id_, event_id, actor, action_type, payload, previous_hash, payload_hash, hash_):
    return SimpleNamespace(
        id=id_,
        event_id=event_id,
        actor=actor,
        action_type=action_type,
        payload=payload,
        previous_hash=previous_hash,
        payload_hash=payload_hash,
        hash=hash_,
    )


# ---------------------------------------------------------------------------
# append_audit_event tests
# ---------------------------------------------------------------------------

def test_append_genesis_event():
    db = _make_db_with_events([])
    event = append_audit_event(db, "SYSTEM", "NEGOTIATION_CREATED", {"negotiation_id": "N1"})
    assert event.previous_hash == "GENESIS"
    assert event.event_id.startswith("EVT-")
    assert len(event.payload_hash) == 64
    assert len(event.hash) == 64
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_append_chained_event():
    payload1 = {"negotiation_id": "N1"}
    ph1, h1 = compute_event_hash("GENESIS", payload1)
    first_event = _make_event(1, "EVT-aaa", "SYSTEM", "NEGOTIATION_CREATED", payload1, "GENESIS", ph1, h1)

    db = _make_db_with_events([first_event])
    event2 = append_audit_event(db, "HUMAN", "APPROVAL_GRANTED", {"approval_id": "APR-1"})
    assert event2.previous_hash == h1
    expected_ph2, expected_h2 = compute_event_hash(h1, {"approval_id": "APR-1"})
    assert event2.payload_hash == expected_ph2
    assert event2.hash == expected_h2


def test_append_event_optional_fields():
    db = _make_db_with_events([])
    event = append_audit_event(
        db, "MERCHANT_AGENT", "ORDER_CREATED", {"order_id": "ORD-1"},
        policy_version="1.0", negotiation_id="NEG-1", razorpay_entity_id="rzp_123"
    )
    assert event.policy_version == "1.0"
    assert event.negotiation_id == "NEG-1"
    assert event.razorpay_entity_id == "rzp_123"


# ---------------------------------------------------------------------------
# validate_audit_chain tests
# ---------------------------------------------------------------------------

def _build_valid_chain(n: int):
    events = []
    prev_hash = "GENESIS"
    for i in range(n):
        payload = {"step": i}
        ph, h = compute_event_hash(prev_hash, payload)
        events.append(_make_event(i + 1, f"EVT-{i:03d}", "SYSTEM", "TEST", payload, prev_hash, ph, h))
        prev_hash = h
    return events


def test_validate_empty_chain():
    db = _make_db_with_events([])
    result = validate_audit_chain(db)
    assert result == {"valid": True, "events_checked": 0, "first_invalid_event_id": None}


def test_validate_valid_chain():
    events = _build_valid_chain(5)
    db = _make_db_with_events(events)
    result = validate_audit_chain(db)
    assert result["valid"] is True
    assert result["events_checked"] == 5
    assert result["first_invalid_event_id"] is None


def test_validate_tampered_payload():
    events = _build_valid_chain(3)
    # Tamper: change payload of event[1] without updating hashes
    tampered = SimpleNamespace(**vars(events[1]))
    tampered.payload = {"step": 999}  # changed but payload_hash not updated
    events[1] = tampered

    db = _make_db_with_events(events)
    result = validate_audit_chain(db)
    assert result["valid"] is False
    assert result["first_invalid_event_id"] == "EVT-001"


def test_validate_tampered_hash():
    events = _build_valid_chain(3)
    # Tamper: corrupt the stored hash of event[0]
    tampered = SimpleNamespace(**vars(events[0]))
    tampered.hash = "deadbeef" * 8
    events[0] = tampered

    db = _make_db_with_events(events)
    result = validate_audit_chain(db)
    assert result["valid"] is False
    assert result["first_invalid_event_id"] == "EVT-000"


def test_validate_broken_chain_link():
    events = _build_valid_chain(3)
    # Break the chain: event[1].previous_hash doesn't match event[0].hash
    tampered = SimpleNamespace(**vars(events[1]))
    tampered.previous_hash = "wronghash"
    events[1] = tampered

    db = _make_db_with_events(events)
    result = validate_audit_chain(db)
    assert result["valid"] is False
    assert result["first_invalid_event_id"] == "EVT-001"


def test_validate_deletion_detected():
    # Simulate deletion: remove event[1] from a 3-event chain
    # event[2].previous_hash now won't match event[0].hash
    events = _build_valid_chain(3)
    events_after_deletion = [events[0], events[2]]  # event[1] deleted

    db = _make_db_with_events(events_after_deletion)
    result = validate_audit_chain(db)
    assert result["valid"] is False
    assert result["first_invalid_event_id"] == "EVT-002"


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

def test_api_list_audit_events():
    from app.main import app
    from app.database import get_db

    events = _build_valid_chain(2)

    # Make query().order_by().offset().limit().all() work
    db = MagicMock()
    q = MagicMock()
    order_mock = MagicMock()
    offset_mock = MagicMock()
    limit_mock = MagicMock()

    limit_mock.all.return_value = events
    offset_mock.limit.return_value = limit_mock
    order_mock.offset.return_value = offset_mock
    q.order_by.return_value = order_mock
    db.query.return_value = q

    # Add required attributes to SimpleNamespace events for serialization
    for e in events:
        e.timestamp = None
        e.policy_version = None
        e.negotiation_id = None
        e.razorpay_entity_id = None
        e.created_at = None

    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)
    response = client.get("/api/v1/audit/")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["event_id"] == "EVT-000"


def test_api_verify_valid_chain():
    from app.main import app
    from app.database import get_db

    events = _build_valid_chain(3)

    db = MagicMock()
    q = MagicMock()
    order_mock = MagicMock()
    order_mock.all.return_value = events
    q.order_by.return_value = order_mock
    db.query.return_value = q

    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)
    response = client.get("/api/v1/audit/verify")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["events_checked"] == 3


def test_api_verify_invalid_chain():
    from app.main import app
    from app.database import get_db

    events = _build_valid_chain(3)
    tampered = SimpleNamespace(**vars(events[1]))
    tampered.payload = {"step": 999}
    events[1] = tampered

    db = MagicMock()
    q = MagicMock()
    order_mock = MagicMock()
    order_mock.all.return_value = events
    q.order_by.return_value = order_mock
    db.query.return_value = q

    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)
    response = client.get("/api/v1/audit/verify")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["first_invalid_event_id"] == "EVT-001"
