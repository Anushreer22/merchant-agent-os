from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.catalog import CatalogVersion
from app.models.policy import Policy
from app.models.buyer import Buyer
from app.services.policy_service import seed_default_policy

PRODUCTS_DATA = [
    {
        "product_id": "SUB_PRO_001",
        "name": "Pro Annual Subscription",
        "description": "Annual professional subscription with all core features.",
        "category": "subscriptions",
        "base_price": 10000,
        "currency": "INR",
        "inventory": 1000,
        "margin_floor": 0.30,
        "discount_rules": {"max_auto_discount": 0.15, "max_approved_discount": 0.20},
        "volume_discount_rules": {"10+": 0.05, "20+": 0.10},
        "bundle_rules": {"SUPPORT_001": 0.10, "ANALYTICS_001": 0.15},
        "upsell_options": [
            {"product_id": "SUPPORT_001", "bundle_discount": 0.10},
            {"product_id": "ANALYTICS_001", "bundle_discount": 0.15},
        ],
        "availability": True,
        "metadata": {"tier": "pro", "renewal": "annual"},
    },
    {
        "product_id": "SUPPORT_001",
        "name": "Premium Support",
        "description": "24/7 priority support with dedicated agent.",
        "category": "support",
        "base_price": 3000,
        "currency": "INR",
        "inventory": 500,
        "margin_floor": 0.40,
        "discount_rules": {"max_auto_discount": 0.10, "max_approved_discount": 0.15},
        "volume_discount_rules": {},
        "bundle_rules": {},
        "upsell_options": [],
        "availability": True,
        "metadata": {},
    },
    {
        "product_id": "ANALYTICS_001",
        "name": "Analytics Add-on",
        "description": "Advanced analytics and reporting module.",
        "category": "addons",
        "base_price": 5000,
        "currency": "INR",
        "inventory": 800,
        "margin_floor": 0.35,
        "discount_rules": {"max_auto_discount": 0.10, "max_approved_discount": 0.15},
        "volume_discount_rules": {},
        "bundle_rules": {},
        "upsell_options": [],
        "availability": True,
        "metadata": {},
    },
    {
        "product_id": "ENT_PLAN_001",
        "name": "Enterprise Plan",
        "description": "Enterprise-grade plan with unlimited seats and custom integrations.",
        "category": "subscriptions",
        "base_price": 50000,
        "currency": "INR",
        "inventory": 100,
        "margin_floor": 0.25,
        "discount_rules": {"max_auto_discount": 0.10, "max_approved_discount": 0.15},
        "volume_discount_rules": {"5+": 0.05},
        "bundle_rules": {},
        "upsell_options": [{"product_id": "SUPPORT_001", "bundle_discount": 0.20}],
        "availability": True,
        "metadata": {"tier": "enterprise"},
    },
    {
        "product_id": "PRIORITY_SUPPORT_001",
        "name": "Priority Support",
        "description": "Priority queue and 4-hour response SLA.",
        "category": "support",
        "base_price": 8000,
        "currency": "INR",
        "inventory": 300,
        "margin_floor": 0.45,
        "discount_rules": {"max_auto_discount": 0.05, "max_approved_discount": 0.10},
        "volume_discount_rules": {},
        "bundle_rules": {},
        "upsell_options": [],
        "availability": True,
        "metadata": {},
    },
]


def seed_products(db: Session) -> None:
    if db.query(Product).count() > 0:
        return
    for p in PRODUCTS_DATA:
        db.add(Product(**p))
    db.commit()


def seed_catalog(db: Session) -> None:
    products_out = []
    for p in db.query(Product).all():
        products_out.append(
            {
                "product_id": p.product_id,
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "base_price": float(p.base_price),
                "currency": p.currency,
                "inventory": p.inventory,
                "margin_floor": float(p.margin_floor),
                "discount_rules": p.discount_rules,
                "volume_discount_rules": p.volume_discount_rules,
                "bundle_rules": p.bundle_rules,
                "upsell_options": p.upsell_options,
                "availability": p.availability,
                "metadata": p.meta_info,
            }
        )

    if db.query(CatalogVersion).count() > 0:
        return
    catalog = CatalogVersion(
        version="1.0",
        catalog_data={"products": products_out},
        is_active=True,
    )
    db.add(catalog)
    db.commit()


def seed_default_buyer(db: Session) -> None:
    if db.query(Buyer).count() > 0:
        return
    db.add(
        Buyer(
            buyer_id="BUYER_DEFAULT_001",
            name="Default AI Buyer",
            budget=85000,
            currency="INR",
            max_single_transaction=85000,
            preferred_categories=["subscriptions"],
            negotiation_strategy="balanced",
        )
    )
    db.commit()


def seed_all(db: Session) -> None:
    seed_default_policy(db)
    seed_products(db)
    seed_catalog(db)
    seed_default_buyer(db)
