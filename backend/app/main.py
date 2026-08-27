from fastapi import FastAPI
from app.api.health import router as health_router
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health_router, prefix=f"{settings.API_V1_PREFIX}/health", tags=["health"])