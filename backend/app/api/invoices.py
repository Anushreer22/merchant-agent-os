from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.negotiation import Negotiation
from app.models.user import User
from app.services.auth_service import get_current_user, require_role

router = APIRouter()

INVOICE_DIR = Path(__file__).parent.parent.parent / "static" / "invoices"


@router.get("/{order_id}/invoice")
def download_invoice(
    order_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order.invoice_url:
        raise HTTPException(status_code=404, detail="Invoice not yet generated")

    if user.role in ("merchant", "admin"):
        pass
    else:
        negotiation = db.query(Negotiation).filter(Negotiation.negotiation_id == order.negotiation_id).first()
        if not negotiation:
            raise HTTPException(status_code=403, detail="Not authorized to access this invoice")

    filepath = INVOICE_DIR / f"{order_id}.pdf"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Invoice file not found")

    return FileResponse(str(filepath), media_type="application/pdf",
                        filename=f"invoice_{order_id}.pdf")
