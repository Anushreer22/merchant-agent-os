from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, func
from app.database import Base

class CatalogVersion(Base):
    __tablename__ = "catalog_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True, nullable=False)
    catalog_data = Column(JSON, nullable=False)  # snapshot of products
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())