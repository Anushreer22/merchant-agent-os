from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from sqlalchemy.orm import Session
from app.api.health import router as health_router
from app.api.catalog import router as catalog_router
from app.api.policy import router as policy_router
from app.api.negotiations import router as negotiations_router
from app.api.payments import router as payments_router
from app.api.webhooks import router as webhooks_router
from app.api.agent import router as agent_router
from app.api.approvals import router as approvals_router
from app.api.buyers import router as buyers_router
from app.api.simulate import router as simulate_router
from app.api.audit import router as audit_router
from app.api.failures import router as failures_router
from app.api.x402 import router as x402_router
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=f"{settings.API_V1_PREFIX}/health", tags=["health"])
app.include_router(catalog_router, prefix=f"{settings.API_V1_PREFIX}/catalog", tags=["catalog"])
app.include_router(policy_router, prefix=f"{settings.API_V1_PREFIX}/policy", tags=["policy"])
app.include_router(negotiations_router, prefix=f"{settings.API_V1_PREFIX}/negotiations", tags=["negotiations"])
app.include_router(payments_router, prefix=f"{settings.API_V1_PREFIX}/payments", tags=["payments"])
app.include_router(webhooks_router, prefix=f"{settings.API_V1_PREFIX}/webhooks", tags=["webhooks"])
app.include_router(agent_router, prefix=f"{settings.API_V1_PREFIX}/agent", tags=["agent"])
app.include_router(approvals_router, prefix=f"{settings.API_V1_PREFIX}/approvals", tags=["approvals"])
app.include_router(buyers_router, prefix=f"{settings.API_V1_PREFIX}/buyers", tags=["buyers"])
app.include_router(simulate_router, prefix=f"{settings.API_V1_PREFIX}/simulate", tags=["simulate"])
app.include_router(audit_router, prefix=f"{settings.API_V1_PREFIX}/audit", tags=["audit"])
app.include_router(failures_router, prefix=f"{settings.API_V1_PREFIX}/simulate/failures", tags=["failures"])
app.include_router(x402_router, prefix=f"{settings.API_V1_PREFIX}/x402", tags=["x402"])


# ---------------------------------------------------------------------------
# Stats endpoint — aggregates counts for the dashboard
# ---------------------------------------------------------------------------
from app.database import get_db
from app.models.negotiation import Negotiation
from app.models.order import Order
from app.models.approval import Approval
from app.models.audit import AuditEvent


@app.get(f"{settings.API_V1_PREFIX}/stats", tags=["stats"])
def get_stats(db: Session = Depends(get_db)):
    total_negotiations = db.query(Negotiation).count()
    allowed = db.query(Negotiation).filter(Negotiation.decision == "ALLOWED").count()
    rejected = db.query(Negotiation).filter(Negotiation.decision == "REJECTED").count()
    pending_approvals = db.query(Approval).filter(Approval.status == "PENDING").count()
    total_orders = db.query(Order).count()
    paid_orders = db.query(Order).filter(Order.status == "paid").count()
    audit_count = db.query(AuditEvent).count()

    from sqlalchemy import func as sqlfunc
    revenue_row = db.query(sqlfunc.sum(Order.amount)).filter(Order.status == "paid").scalar()
    revenue = float(revenue_row or 0)

    discount_row = db.query(sqlfunc.avg(Negotiation.final_discount)).scalar()
    avg_discount = round(float(discount_row or 0) * 100, 2)

    return {
        "total_negotiations": total_negotiations,
        "allowed_negotiations": allowed,
        "rejected_negotiations": rejected,
        "pending_approvals": pending_approvals,
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "revenue_inr": revenue,
        "avg_discount_pct": avg_discount,
        "audit_events": audit_count,
    }
