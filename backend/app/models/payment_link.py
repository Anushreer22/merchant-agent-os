from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class PaymentLink(Base):
    __tablename__ = "payment_links"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(String, unique=True, index=True, nullable=False)
    order_id = Column(String, index=True, nullable=False)
    negotiation_id = Column(String, index=True, nullable=False)
    short_url = Column(String, nullable=False)
    status = Column(String, default="created", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
