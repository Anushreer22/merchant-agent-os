import pytest
from types import SimpleNamespace
from app.policy.engine import (
    check_discount_policy,
    check_margin_policy,
    check_inventory_policy,
    check_transaction_limit,
    check_approval_requirement,
    calculate_allowed_counter_offer,
    evaluate_action,
)

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
        product_id="TEST_001",
        base_price=10000,
        inventory=50,
        margin_floor=0.30,
        discount_rules={},
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# --- check_discount_policy ---

def test_discount_within_auto_limit():
    product = make_product()
    result = check_discount_policy(product, 0.10, POLICY)
    assert result["passed"] is True
    assert result["reason_code"] == "WITHIN_POLICY"


def test_discount_within_approved_limit():
    product = make_product()
    result = check_discount_policy(product, 0.18, POLICY)
    assert result["passed"] is True
    assert result["reason_code"] == "WITHIN_POLICY"


def test_discount_exceeds_human_limit():
    product = make_product()
    result = check_discount_policy(product, 0.25, POLICY)
    assert result["passed"] is False
    assert result["reason_code"] == "DISCOUNT_EXCEEDS_LIMIT"


# --- check_margin_policy ---

def test_margin_ok():
    product = make_product(base_price=10000, margin_floor=0.30)
    # final_unit_price = 10000 * (1 - 0.15) = 8500; margin_after = 0.85 >= 0.30
    result = check_margin_policy(product, 8500, POLICY)
    assert result["passed"] is True
    assert result["reason_code"] == "MARGIN_OK"


def test_margin_below_floor():
    product = make_product(base_price=10000, margin_floor=0.80)
    # final_unit_price = 1000; margin_after = 0.10 < 0.80
    result = check_margin_policy(product, 1000, POLICY)
    assert result["passed"] is False
    assert result["reason_code"] == "MARGIN_BELOW_FLOOR"


# --- check_inventory_policy ---

def test_inventory_ok():
    product = make_product(inventory=50)
    result = check_inventory_policy(product, 10)
    assert result["passed"] is True
    assert result["reason_code"] == "INVENTORY_OK"


def test_inventory_insufficient():
    product = make_product(inventory=5)
    result = check_inventory_policy(product, 10)
    assert result["passed"] is False
    assert result["reason_code"] == "INSUFFICIENT_INVENTORY"


# --- check_transaction_limit ---

def test_amount_within_limit():
    result = check_transaction_limit(4000, POLICY)
    assert result["passed"] is True
    assert result["reason_code"] == "AMOUNT_WITHIN_LIMIT"


def test_amount_exceeds_threshold():
    result = check_transaction_limit(6000, POLICY)
    assert result["passed"] is False
    assert result["reason_code"] == "AMOUNT_EXCEEDS_APPROVAL_THRESHOLD"


# --- check_approval_requirement ---

def test_approval_required_high_discount():
    product = make_product()
    assert check_approval_requirement(product, 5, 0.18, 1000, POLICY) is True


def test_approval_required_high_quantity():
    product = make_product()
    assert check_approval_requirement(product, 25, 0.10, 1000, POLICY) is True


def test_approval_required_high_amount():
    product = make_product()
    assert check_approval_requirement(product, 5, 0.10, 6000, POLICY) is True


def test_no_approval_required():
    product = make_product()
    assert check_approval_requirement(product, 5, 0.10, 1000, POLICY) is False


# --- calculate_allowed_counter_offer ---

def test_counter_offer_within_auto():
    product = make_product()
    assert calculate_allowed_counter_offer(product, POLICY, 0.10) == 0.15


def test_counter_offer_within_approved():
    product = make_product()
    assert calculate_allowed_counter_offer(product, POLICY, 0.18) == 0.20


def test_counter_offer_exceeds_approved():
    product = make_product()
    assert calculate_allowed_counter_offer(product, POLICY, 0.30) == 0.15


# --- evaluate_action ---

def test_evaluate_allowed():
    # base_price=1000, discount=0.10 -> final=900, total=900 < 5000 threshold
    product = make_product(base_price=1000, inventory=50, margin_floor=0.30)
    action = {"product_id": "TEST_001", "quantity": 1, "requested_discount": 0.10}
    result = evaluate_action(action, product, POLICY)
    assert result["decision"] == "ALLOWED"
    assert result["reason_code"] == "WITHIN_POLICY"
    assert result["requires_human_approval"] is False


def test_evaluate_approval_required_discount():
    product = make_product(base_price=10000, inventory=50, margin_floor=0.30)
    action = {"product_id": "TEST_001", "quantity": 1, "requested_discount": 0.18}
    result = evaluate_action(action, product, POLICY)
    assert result["decision"] == "APPROVAL_REQUIRED"
    assert result["requires_human_approval"] is True
    assert result["reason_code"] == "APPROVAL_REQUIRED"


def test_evaluate_rejected_exceeds_limit():
    product = make_product(base_price=10000, inventory=50, margin_floor=0.30)
    action = {"product_id": "TEST_001", "quantity": 1, "requested_discount": 0.25}
    result = evaluate_action(action, product, POLICY)
    assert result["decision"] == "REJECTED"
    assert result["reason_code"] == "DISCOUNT_EXCEEDS_LIMIT"
    assert result["counter_offer"] is not None


def test_evaluate_rejected_margin():
    product = make_product(base_price=10000, inventory=50, margin_floor=0.90)
    action = {"product_id": "TEST_001", "quantity": 1, "requested_discount": 0.15}
    result = evaluate_action(action, product, POLICY)
    assert result["decision"] == "REJECTED"
    assert result["reason_code"] == "MARGIN_BELOW_FLOOR"


def test_evaluate_rejected_inventory():
    product = make_product(base_price=10000, inventory=2, margin_floor=0.30)
    action = {"product_id": "TEST_001", "quantity": 10, "requested_discount": 0.10}
    result = evaluate_action(action, product, POLICY)
    assert result["decision"] == "REJECTED"
    assert result["reason_code"] == "INSUFFICIENT_INVENTORY"


def test_evaluate_approval_required_high_amount():
    product = make_product(base_price=10000, inventory=50, margin_floor=0.30)
    # 10 * 10000 * 0.90 = 90000 > 5000 threshold
    action = {"product_id": "TEST_001", "quantity": 10, "requested_discount": 0.10}
    result = evaluate_action(action, product, POLICY)
    assert result["decision"] == "APPROVAL_REQUIRED"
    assert result["reason_code"] == "APPROVAL_REQUIRED"
