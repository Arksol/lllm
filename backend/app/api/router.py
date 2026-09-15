from __future__ import annotations

from fastapi import APIRouter

from app.analysis.router import router as analysis_router
from app.security_scan.scanner import available_tools
from app.settings.router import router as settings_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(analysis_router)
api_router.include_router(settings_router)


@api_router.get("/health", tags=["salud"])
def health() -> dict:
    return {"status": "ok"}


@api_router.get("/health/ready", tags=["salud"])
def ready() -> dict:
    from app.database import engine
    from sqlalchemy import text

    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        database = "ok"
    except Exception as exc:  # noqa: BLE001
        database = f"error: {exc}"

    return {
        "status": "ok" if database == "ok" else "degradado",
        "database": database,
        "security_tools": available_tools(),
    }
