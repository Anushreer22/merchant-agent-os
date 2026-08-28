def _get(rules: dict, key: str, fallback):
    return rules.get(key, fallback)


def _rules(policy) -> dict:
    return policy.rules if hasattr(policy, "rules") else policy


def _version(policy) -> str:
    return policy.version if hasattr(policy, "version") else "unknown"


def _effective_discount_limits(product, rules: dict) -> tuple[float, float]:
    dr = product.discount_rules or {}
    max_auto = float(dr.get("max_auto_discount", _get(rules, "max_auto_discount", 0.15)))
    max_approved = float(dr.get("max_approved_discount", _get(rules, "max_human_approved_discount", 0.20)))
    return max_auto, max_approved


def check_discount_policy(product, requested_discount: float, policy) -> dict:
    rules = _rules(policy)
    _, max_approved = _effective_discount_limits(product, rules)
    passed = requested_discount <= max_approved
    return {"reason_code": "WITHIN_POLICY" if passed else "DISCOUNT_EXCEEDS_LIMIT", "passed": passed}


def check_margin_policy(product, final_unit_price: float, policy) -> dict:
    rules = _rules(policy)
    floor = float(product.margin_floor) if product.margin_floor is not None else float(_get(rules, "margin_floor", 0.30))
    base = float(product.base_price)
    # margin_after_discount = final_unit_price / base_price; must be >= margin_floor
    # e.g. margin_floor=0.30 means price cannot drop below 30% of base (max 70% discount)
    margin_after = round(final_unit_price / base, 4) if base > 0 else 1.0
    passed = margin_after >= floor
    return {
        "reason_code": "MARGIN_OK" if passed else "MARGIN_BELOW_FLOOR",
        "passed": passed,
        "margin_after_discount": margin_after,
    }


def check_inventory_policy(product, quantity: int) -> dict:
    passed = quantity <= product.inventory
    return {"reason_code": "INVENTORY_OK" if passed else "INSUFFICIENT_INVENTORY", "passed": passed}


def check_transaction_limit(amount: float, policy) -> dict:
    rules = _rules(policy)
    threshold = float(_get(rules, "human_approval_amount", 5000))
    passed = amount <= threshold
    return {"reason_code": "AMOUNT_WITHIN_LIMIT" if passed else "AMOUNT_EXCEEDS_APPROVAL_THRESHOLD", "passed": passed}


def check_approval_requirement(product, quantity: int, requested_discount: float, amount: float, policy) -> bool:
    rules = _rules(policy)
    max_auto, _ = _effective_discount_limits(product, rules)
    max_qty = int(_get(rules, "max_quantity_without_approval", 20))
    threshold = float(_get(rules, "human_approval_amount", 5000))
    return requested_discount > max_auto or quantity > max_qty or amount > threshold


def calculate_allowed_counter_offer(product, policy, requested_discount: float) -> float:
    rules = _rules(policy)
    max_auto, max_approved = _effective_discount_limits(product, rules)
    if requested_discount <= max_auto:
        return max_auto
    if requested_discount <= max_approved:
        return max_approved
    return max_auto


def evaluate_action(action: dict, product, policy) -> dict:
    rules = _rules(policy)
    requested_discount = float(action.get("requested_discount", 0.0))
    quantity = int(action.get("quantity", 1))
    base_price = float(product.base_price)

    final_unit_price = base_price * (1 - requested_discount)
    total_amount = final_unit_price * quantity

    max_auto, _ = _effective_discount_limits(product, rules)
    inv = check_inventory_policy(product, quantity)
    disc = check_discount_policy(product, requested_discount, rules)
    margin = check_margin_policy(product, final_unit_price, rules)
    needs_approval = check_approval_requirement(product, quantity, requested_discount, total_amount, rules)

    margin_after = margin["margin_after_discount"]
    allowed_discount = calculate_allowed_counter_offer(product, rules, requested_discount)
    counter = {"discount": allowed_discount, "final_unit_price": round(base_price * (1 - allowed_discount), 2)}

    if not inv["passed"]:
        return _build("REJECTED", False, max_auto, margin_after, None, _version(policy), "INSUFFICIENT_INVENTORY")
    if not disc["passed"]:
        return _build("REJECTED", False, max_auto, margin_after, counter, _version(policy), "DISCOUNT_EXCEEDS_LIMIT")
    if not margin["passed"]:
        return _build("REJECTED", False, max_auto, margin_after, counter, _version(policy), "MARGIN_BELOW_FLOOR")
    if needs_approval:
        return _build("APPROVAL_REQUIRED", True, max_auto, margin_after, counter, _version(policy), "APPROVAL_REQUIRED")
    return _build("ALLOWED", False, max_auto, margin_after, None, _version(policy), "WITHIN_POLICY")


def _build(decision, requires_approval, max_auto, margin_after, counter_offer, policy_version, reason_code) -> dict:
    return {
        "decision": decision,
        "requires_human_approval": requires_approval,
        "maximum_allowed_discount": max_auto,
        "margin_after_discount": margin_after,
        "counter_offer": counter_offer,
        "policy_version": policy_version,
        "reason_code": reason_code,
    }
