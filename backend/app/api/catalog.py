from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.catalog_service import get_active_catalog
from app.schemas.catalog import CatalogResponse

router = APIRouter()

@router.get("/", response_model=CatalogResponse)
def read_catalog(db: Session = Depends(get_db)):
    catalog = get_active_catalog(db)
    if not catalog:
        raise HTTPException(status_code=404, detail="No active catalog found")
    return catalog
