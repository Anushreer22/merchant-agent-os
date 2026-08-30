from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="merchant", nullable=False)  # admin | merchant | buyer
    merchant_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
