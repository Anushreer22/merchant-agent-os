import os
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.negotiation import Negotiation
from app.models.buyer import Buyer
from app.models.product import Product

INVOICE_DIR = Path(__file__).parent.parent.parent / "static" / "invoices"
INVOICE_DIR.mkdir(parents=True, exist_ok=True)


def generate_invoice(order_id: str, order_data: dict) -> str:
    """Generate a PDF invoice and return the relative URL path."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
    except ImportError:
        return ""

    filename = f"{order_id}.pdf"
    filepath = INVOICE_DIR / filename

    doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("MERCHANT AGENT OS", styles["Title"]))
    story.append(Paragraph("Tax Invoice / Receipt", styles["Heading2"]))
    story.append(Spacer(1, 0.5*cm))

    meta = [
        ["Invoice #", order_id],
        ["Date", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
        ["Status", order_data.get("status", "").upper()],
    ]
    meta_table = Table(meta, colWidths=[4*cm, 12*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Order Details", styles["Heading3"]))
    items = [
        ["Field", "Value"],
        ["Buyer ID", order_data.get("buyer_id", "—")],
        ["Product ID", order_data.get("product_id", "—")],
        ["Quantity", str(order_data.get("quantity", "—"))],
        ["Discount Applied", f"{float(order_data.get('discount', 0)) * 100:.1f}%"],
        ["Currency", order_data.get("currency", "INR")],
        ["Total Amount", f"{order_data.get('currency', 'INR')} {float(order_data.get('amount', 0)):,.2f}"],
    ]
    items_table = Table(items, colWidths=[6*cm, 10*cm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Thank you for your business.", styles["Normal"]))

    doc.build(story)
    return f"/static/invoices/{filename}"


def generate_invoice_pdf(
    db: Session,
    order: Order,
    negotiation: Negotiation,
    buyer: Buyer,
    product: Product,
) -> str:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
    except ImportError:
        return ""

    filename = f"{order.order_id}.pdf"
    filepath = INVOICE_DIR / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("MERCHANT AGENT OS", styles["Title"]))
    story.append(Paragraph("Tax Invoice / Receipt", styles["Heading2"]))
    story.append(Spacer(1, 0.5 * cm))

    meta = [
        ["Invoice #", order.order_id],
        ["Date", order.created_at.strftime("%Y-%m-%d %H:%M UTC") if order.created_at else "—"],
        ["Status", order.status.upper()],
        ["Payment", order.status.upper()],
    ]
    meta_table = Table(meta, colWidths=[4 * cm, 12 * cm])
    meta_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Buyer Details", styles["Heading3"]))
    buyer_rows = [
        ["Field", "Value"],
        ["Buyer ID", buyer.buyer_id],
        ["Name", buyer.name or "—"],
        ["Currency", buyer.currency or "INR"],
    ]
    buyer_table = Table(buyer_rows, colWidths=[6 * cm, 10 * cm])
    buyer_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fdfa")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ccfbf1")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(buyer_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Product Details", styles["Heading3"]))
    product_rows = [
        ["Field", "Value"],
        ["Product ID", product.product_id],
        ["Name", product.name],
        ["Quantity", str(negotiation.quantity)],
        ["Unit Price", f"{product.currency} {float(product.base_price):,.2f}"],
        ["Discount", f"{float(negotiation.final_discount) * 100:.1f}%"],
        ["Final Amount", f"{order.currency} {float(order.amount):,.2f}"],
    ]
    product_table = Table(product_rows, colWidths=[6 * cm, 10 * cm])
    product_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(product_table)
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Thank you for your business.", styles["Normal"]))

    doc.build(story)
    return f"/static/invoices/{filename}"

