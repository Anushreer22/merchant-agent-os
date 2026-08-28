import json
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi import HTTPException

from app.agents.merchant_agent import MerchantAgent, _parse_llm_response, _enrich_reply


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_llm_response(product_id="SUB_PRO_001", quantity=1, requested_discount=0.10,
                      message="Your request is being evaluated."):
    content = json.dumps({
        "product_id": product_id,
        "quantity": quantity,
        "requested_discount": requested_discount,
        "message": message,
    })
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


def make_negotiation_result(decision="ALLOWED", requires_approval=False,
                             max_discount=0.15, counter_offer=None,
                             reason_code="WITHIN_POLICY"):
    return {
        "negotiation_id": "neg-test-001",
        "decision": decision,
        "requires_human_approval": requires_approval,
        "maximum_allowed_discount": max_discount,
        "counter_offer": counter_offer,
        "policy_version": "1.0",
        "reason_code": reason_code,
        "final_price": 900.0,
        "currency": "INR",
        "created_at": datetime.now(timezone.utc),
    }


# ---------------------------------------------------------------------------
# _parse_llm_response unit tests
# ---------------------------------------------------------------------------

def test_parse_valid_json():
    raw = json.dumps({
        "product_id": "PROD_001",
        "quantity": 3,
        "requested_discount": 0.15,
        "message": "Hello",
    })
    result = _parse_llm_response(raw)
    assert result["product_id"] == "PROD_001"
    assert result["quantity"] == 3
    assert result["requested_discount"] == pytest.approx(0.15)


def test_parse_clamps_discount_above_1():
    raw = json.dumps({"product_id": "P", "quantity": 1, "requested_discount": 1.5, "message": "hi"})
    result = _parse_llm_response(raw)
    assert result["requested_discount"] == pytest.approx(1.0)


def test_parse_clamps_discount_below_0():
    raw = json.dumps({"product_id": "P", "quantity": 1, "requested_discount": -0.5, "message": "hi"})
    result = _parse_llm_response(raw)
    assert result["requested_discount"] == pytest.approx(0.0)


def test_parse_quantity_defaults_to_1_when_zero():
    raw = json.dumps({"product_id": "P", "quantity": 0, "requested_discount": 0.1, "message": "hi"})
    result = _parse_llm_response(raw)
    assert result["quantity"] == 1


def test_parse_missing_key_raises():
    raw = json.dumps({"product_id": "P", "quantity": 1})  # missing required keys
    with pytest.raises(ValueError):
        _parse_llm_response(raw)


def test_parse_invalid_json_raises():
    with pytest.raises((ValueError, Exception)):
        _parse_llm_response("not json at all !!!")


def test_parse_extracts_json_from_markdown():
    raw = '```json\n{"product_id":"P","quantity":2,"requested_discount":0.1,"message":"hi"}\n```'
    result = _parse_llm_response(raw)
    assert result["product_id"] == "P"


# ---------------------------------------------------------------------------
# _enrich_reply unit tests
# ---------------------------------------------------------------------------

def test_enrich_allowed():
    reply = _enrich_reply("Your request is noted.", {"decision": "ALLOWED", "counter_offer": None, "reason_code": "WITHIN_POLICY"})
    assert "approved" in reply.lower()


def test_enrich_approval_required():
    reply = _enrich_reply("Noted.", {"decision": "APPROVAL_REQUIRED", "counter_offer": None, "reason_code": "APPROVAL_REQUIRED"})
    assert "approval" in reply.lower()


def test_enrich_rejected_with_counter():
    reply = _enrich_reply("Noted.", {
        "decision": "REJECTED",
        "counter_offer": {"discount": 0.15, "final_unit_price": 850.0},
        "reason_code": "DISCOUNT_EXCEEDS_LIMIT",
    })
    assert "15.0%" in reply


def test_enrich_rejected_no_counter():
    reply = _enrich_reply("Noted.", {"decision": "REJECTED", "counter_offer": None, "reason_code": "INSUFFICIENT_INVENTORY"})
    assert "cannot be fulfilled" in reply.lower()


# ---------------------------------------------------------------------------
# MerchantAgent.negotiate integration tests (fully mocked)
# ---------------------------------------------------------------------------

agent = MerchantAgent()


def _run_negotiate(llm_response, negotiation_result, buyer_message="I want SUB_PRO_001 with 10% off"):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = llm_response
    with patch("app.agents.merchant_agent._get_openai_client", return_value=mock_client):
        with patch("app.agents.merchant_agent.create_negotiation", return_value=negotiation_result):
            return agent.negotiate(buyer_message=buyer_message, db=MagicMock())


def test_negotiate_allowed():
    llm_resp = make_llm_response(requested_discount=0.10)
    neg_result = make_negotiation_result(decision="ALLOWED", reason_code="WITHIN_POLICY")
    result = _run_negotiate(llm_resp, neg_result)

    assert result["intent"]["product_id"] == "SUB_PRO_001"
    assert result["intent"]["requested_discount"] == pytest.approx(0.10)
    assert result["policy_result"]["decision"] == "ALLOWED"
    assert "approved" in result["reply"].lower()


def test_negotiate_approval_required():
    llm_resp = make_llm_response(requested_discount=0.18)
    neg_result = make_negotiation_result(
        decision="APPROVAL_REQUIRED",
        requires_approval=True,
        reason_code="APPROVAL_REQUIRED",
        counter_offer={"discount": 0.15, "final_unit_price": 850.0},
    )
    result = _run_negotiate(llm_resp, neg_result, buyer_message="I want 18% off SUB_PRO_001")

    assert result["policy_result"]["decision"] == "APPROVAL_REQUIRED"
    assert result["policy_result"]["requires_human_approval"] is True
    assert "approval" in result["reply"].lower()


def test_negotiate_rejected_exceeds_limit():
    llm_resp = make_llm_response(requested_discount=0.30)
    neg_result = make_negotiation_result(
        decision="REJECTED",
        reason_code="DISCOUNT_EXCEEDS_LIMIT",
        counter_offer={"discount": 0.15, "final_unit_price": 850.0},
    )
    result = _run_negotiate(llm_resp, neg_result, buyer_message="I want 30% off")

    assert result["policy_result"]["decision"] == "REJECTED"
    assert result["policy_result"]["counter_offer"] is not None
    assert "15.0%" in result["reply"]


def test_negotiate_malformed_llm_output_uses_fallback():
    # LLM returns garbage — agent should fall back gracefully (no product_id → no negotiation)
    choice = MagicMock()
    choice.message.content = "Sorry I cannot help with that."
    bad_response = MagicMock()
    bad_response.choices = [choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = bad_response

    with patch("app.agents.merchant_agent._get_openai_client", return_value=mock_client):
        result = agent.negotiate(buyer_message="???", db=MagicMock())

    assert result["policy_result"] is None
    assert result["intent"]["product_id"] is None
    assert isinstance(result["reply"], str)


def test_negotiate_no_product_id_skips_policy():
    # LLM returns valid JSON but product_id is null
    llm_resp = make_llm_response(product_id=None, message="Please clarify the product.")
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = llm_resp

    with patch("app.agents.merchant_agent._get_openai_client", return_value=mock_client):
        with patch("app.agents.merchant_agent.create_negotiation") as mock_neg:
            result = agent.negotiate(buyer_message="I want a deal", db=MagicMock())

    mock_neg.assert_not_called()
    assert result["policy_result"] is None


def test_negotiate_product_not_found_raises_404():
    llm_resp = make_llm_response(product_id="NONEXISTENT")
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = llm_resp

    with patch("app.agents.merchant_agent._get_openai_client", return_value=mock_client):
        with patch("app.agents.merchant_agent.create_negotiation",
                   side_effect=HTTPException(status_code=404, detail="Product not found")):
            with pytest.raises(HTTPException) as exc:
                agent.negotiate(buyer_message="I want NONEXISTENT", db=MagicMock())

    assert exc.value.status_code == 404
