import json
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI

from app.config import settings
from app.agents.prompts import SYSTEM_PROMPT
from app.services.negotiation_service import create_negotiation

logger = logging.getLogger(__name__)

_FALLBACK_INTENT = {
    "product_id": None,
    "quantity": 1,
    "requested_discount": 0.0,
    "message": "I'm sorry, I couldn't understand your request. Could you please clarify the product and quantity you need?",
}


def _get_openai_client() -> OpenAI:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _parse_llm_response(content: str) -> dict:
    """Parse and validate the JSON returned by the LLM."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from a markdown code block if present
        import re
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError("No valid JSON found in LLM response")

    required = {"product_id", "quantity", "requested_discount", "message"}
    if not required.issubset(data.keys()):
        raise ValueError(f"LLM response missing keys: {required - data.keys()}")

    # Coerce and clamp values
    data["quantity"] = max(1, int(data.get("quantity") or 1))
    data["requested_discount"] = max(0.0, min(1.0, float(data.get("requested_discount") or 0.0)))
    return data


def _enrich_reply(base_reply: str, policy_result: dict) -> str:
    """Append a policy-aware sentence to the LLM's draft reply."""
    decision = policy_result["decision"]
    counter = policy_result.get("counter_offer")

    if decision == "ALLOWED":
        return base_reply + " Your requested discount has been approved."
    if decision == "APPROVAL_REQUIRED":
        return base_reply + " This request requires additional approval and is currently under review."
    if decision == "REJECTED":
        reason = policy_result.get("reason_code", "")
        if counter:
            pct = round(counter["discount"] * 100, 1)
            return (
                base_reply
                + f" Unfortunately, the requested discount cannot be accommodated. "
                f"Our best available offer is {pct}% off."
            )
        return base_reply + f" Unfortunately, this request cannot be fulfilled ({reason})."
    return base_reply


class MerchantAgent:
    def negotiate(self, buyer_message: str, db: Session) -> dict:
        # --- Step 1: LLM extracts intent ---
        intent = self._extract_intent(buyer_message)

        if not intent.get("product_id"):
            return {
                "intent": intent,
                "policy_result": None,
                "reply": intent["message"],
            }

        # --- Step 2: Deterministic policy engine evaluates the action ---
        try:
            negotiation_result = create_negotiation(
                db=db,
                buyer_id="AI_BUYER",
                product_id=intent["product_id"],
                quantity=intent["quantity"],
                requested_discount=intent["requested_discount"],
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Negotiation creation failed: %s", exc)
            raise HTTPException(status_code=500, detail="Negotiation processing error")

        policy_result = {
            "decision": negotiation_result["decision"],
            "requires_human_approval": negotiation_result["requires_human_approval"],
            "maximum_allowed_discount": negotiation_result["maximum_allowed_discount"],
            "counter_offer": negotiation_result["counter_offer"],
            "policy_version": negotiation_result["policy_version"],
            "reason_code": negotiation_result["reason_code"],
            "negotiation_id": negotiation_result["negotiation_id"],
            "final_price": negotiation_result["final_price"],
            "currency": negotiation_result["currency"],
        }

        # --- Step 3: Enrich the LLM's draft reply with the policy outcome ---
        reply = _enrich_reply(intent["message"], policy_result)

        return {
            "intent": {
                "product_id": intent["product_id"],
                "quantity": intent["quantity"],
                "requested_discount": intent["requested_discount"],
            },
            "policy_result": policy_result,
            "reply": reply,
        }

    def _extract_intent(self, buyer_message: str) -> dict:
        try:
            client = _get_openai_client()
            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": buyer_message},
                ],
                temperature=0.0,
                max_tokens=300,
            )
            content = response.choices[0].message.content.strip()
            return _parse_llm_response(content)
        except (RuntimeError, ValueError) as exc:
            logger.warning("LLM intent extraction failed: %s", exc)
            return {**_FALLBACK_INTENT}
        except Exception as exc:
            logger.error("Unexpected LLM error: %s", exc)
            return {**_FALLBACK_INTENT}
