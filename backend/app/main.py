"""Punto de entrada de la API local de LLLM."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings
from app.core import exceptions, logging as log, middleware
from app.database import create_all


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201, ARG001
    log.configure()
    create_all()
    yield


app = FastAPI(
    title="LLLM",
    description="Large Language Learning Model — analiza repositorios con el modelo que elijas.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.debug else None,
)

middleware.install(app)
exceptions.install(app)
app.include_router(api_router)


def main() -> None:
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


if __name__ == "__main__":
    main()
