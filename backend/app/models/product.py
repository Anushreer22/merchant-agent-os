from sqlalchemy import Column, Integer, String, Numeric, Boolean, JSON, DateTime, func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, index=True)
    base_price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    inventory = Column(Integer, default=0)
    margin_floor = Column(Numeric(5, 4), nullable=False)
    discount_rules = Column(JSON, nullable=False)
    volume_discount_rules = Column(JSON, default=dict)
    bundle_rules = Column(JSON, default=dict)
    upsell_options = Column(JSON, default=list)
    availability = Column(Boolean, default=True)
    meta_info = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
