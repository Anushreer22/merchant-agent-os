from sqlalchemy.orm import Session
from app.models.catalog import CatalogVersion
from app.schemas.catalog import CatalogResponse

def get_active_catalog(db: Session) -> CatalogResponse | None:
    catalog = db.query(CatalogVersion).filter(CatalogVersion.is_active == True).order_by(CatalogVersion.id.desc()).first()
    if not catalog:
        return None
    return CatalogResponse(
        version=catalog.version,
        products=catalog.catalog_data.get("products", []),
        active=catalog.is_active,
        created_at=catalog.created_at,
    )
