import csv
import io
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.negotiation import Negotiation
from app.models.user import User
from app.services.auth_service import require_role, get_current_user

router = APIRouter()


@router.get("/analytics")
def analytics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    thirty_days_ago = datetime.now() - timedelta(days=30)

    paid_orders = db.query(Order).filter(
        Order.created_at >= thirty_days_ago,
        Order.status == "paid",
    ).all()
    all_orders = db.query(Order).filter(
        Order.created_at >= thirty_days_ago,
    ).all()
    negs = db.query(Negotiation).filter(
        Negotiation.created_at >= thirty_days_ago,
    ).all()

    if not paid_orders and not all_orders and not negs:
        today = datetime.now()
        mock_ts = []
        for i in range(30):
            d = (today - timedelta(days=29 - i)).strftime("%Y-%m-%d")
            mock_ts.append({
                "date": d,
                "revenue": round(3000 + ((i * 137) % 8000), 2),
                "orders": (i % 4) + 1,
            })
        return {
            "revenue_time_series": mock_ts,
            "discount_distribution": [
                {"range": "0-5%", "count": 10},
                {"range": "6-10%", "count": 8},
                {"range": "11-15%", "count": 5},
                {"range": "16-20%", "count": 2},
                {"range": "21%+", "count": 1},
            ],
            "success_rate": 0.85,
            "demo_data": True,
        }

    ts: dict[str, dict] = {}
    for o in paid_orders:
        if o.created_at:
            d = o.created_at.strftime("%Y-%m-%d")
            ts.setdefault(d, {"date": d, "revenue": 0.0, "orders": 0})
            ts[d]["revenue"] = round(ts[d]["revenue"] + float(o.amount), 2)
            ts[d]["orders"] += 1

    for o in all_orders:
        if o.created_at:
            d = o.created_at.strftime("%Y-%m-%d")
            if d not in ts:
                ts[d] = {"date": d, "revenue": 0.0, "orders": 0}

    revenue_time_series = sorted(ts.values(), key=lambda x: x["date"])

    buckets = {"0-5%": 0, "6-10%": 0, "11-15%": 0, "16-20%": 0, "21%+": 0}
    for n in negs:
        d = float(n.final_discount) * 100
        if d <= 5:
            buckets["0-5%"] += 1
        elif d <= 10:
            buckets["6-10%"] += 1
        elif d <= 15:
            buckets["11-15%"] += 1
        elif d <= 20:
            buckets["16-20%"] += 1
        else:
            buckets["21%+"] += 1

    discount_distribution = [{"range": k, "count": v} for k, v in buckets.items()]

    total = len(all_orders)
    success_rate = round(len(paid_orders) / total, 2) if total else 0.0

    return {
        "revenue_time_series": revenue_time_series,
        "discount_distribution": discount_distribution,
        "success_rate": success_rate,
    }


@router.get("/advanced")
def advanced_stats(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("merchant", "admin")),
):
    order_q = db.query(Order)
    neg_q = db.query(Negotiation)

    if start_date:
        dt_start = datetime.strptime(start_date, "%Y-%m-%d")
        order_q = order_q.filter(Order.created_at >= dt_start)
        neg_q = neg_q.filter(Negotiation.created_at >= dt_start)
    if end_date:
        dt_end = datetime.strptime(end_date, "%Y-%m-%d")
        order_q = order_q.filter(Order.created_at <= dt_end)
        neg_q = neg_q.filter(Negotiation.created_at <= dt_end)

    orders = order_q.all()
    negs = neg_q.all()

    paid = [o for o in orders if o.status == "paid"]
    total_revenue = sum(float(o.amount) for o in paid)
    total_transactions = len(orders)
    success_rate = round(len(paid) / total_transactions * 100, 1) if total_transactions else 0.0
    avg_order_value = round(total_revenue / len(paid), 2) if paid else 0.0
    discount_given = round(sum(float(n.final_discount) * float(n.final_amount) for n in negs), 2)

    # Time series: group paid orders by date
    ts: dict[str, dict] = {}
    for o in paid:
        if o.created_at:
            d = o.created_at.strftime("%Y-%m-%d")
            ts.setdefault(d, {"date": d, "revenue": 0.0, "orders": 0})
            ts[d]["revenue"] = round(ts[d]["revenue"] + float(o.amount), 2)
            ts[d]["orders"] += 1
    time_series = sorted(ts.values(), key=lambda x: x["date"])

    # Discount distribution buckets
    buckets = {"0-5%": 0, "5-10%": 0, "10-15%": 0, "15-20%": 0, "20%+": 0}
    for n in negs:
        d = float(n.final_discount) * 100
        if d <= 5:
            buckets["0-5%"] += 1
        elif d <= 10:
            buckets["5-10%"] += 1
        elif d <= 15:
            buckets["10-15%"] += 1
        elif d <= 20:
            buckets["15-20%"] += 1
        else:
            buckets["20%+"] += 1
    discount_distribution = [{"bucket": k, "count": v} for k, v in buckets.items()]

    return {
        "total_revenue": total_revenue,
        "total_transactions": total_transactions,
        "success_rate": success_rate,
        "discount_given": discount_given,
        "average_order_value": avg_order_value,
        "time_series": time_series,
        "discount_distribution": discount_distribution,
    }


@router.get("/export/transactions")
def export_transactions(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("merchant", "admin")),
):
    orders = db.query(Order).order_by(Order.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["order_id", "negotiation_id", "amount", "currency", "receipt", "status", "created_at"])
    for o in orders:
        writer.writerow([o.order_id, o.negotiation_id, float(o.amount), o.currency,
                         o.receipt, o.status, o.created_at])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )
