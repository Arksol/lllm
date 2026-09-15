"""Manejo de errores: el usuario ve una causa util, nunca una traza interna."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.llm.base import ProviderError
from app.llm.factory import NoModelConfigured
from app.repos.exceptions import RepoError

logger = logging.getLogger("lllm")


def install(app: FastAPI) -> None:
    @app.exception_handler(RepoError)
    async def repo_error(request: Request, exc: RepoError):  # noqa: ANN001, ARG001
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(ProviderError)
    async def provider_error(request: Request, exc: ProviderError):  # noqa: ANN001, ARG001
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(NoModelConfigured)
    async def no_model(request: Request, exc: NoModelConfigured):  # noqa: ANN001, ARG001
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):  # noqa: ANN001
        logger.exception("Error no controlado en %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Algo fallo en la aplicacion. Revisa el registro."},
        )
