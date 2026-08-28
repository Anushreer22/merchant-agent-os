from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.catalog import router as catalog_router
from app.api.policy import router as policy_router
from app.api.negotiations import router as negotiations_router
from app.api.payments import router as payments_router
from app.api.webhooks import router as webhooks_router
from app.api.agent import router as agent_router
from app.api.approvals import router as approvals_router
from app.api.buyers import router as buyers_router
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
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
