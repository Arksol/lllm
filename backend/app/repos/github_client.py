"""Descarga el contenido de un repositorio publico de GitHub.

Se usa el tarball de la API en lugar de git clone: no requiere git instalado,
trae un solo archivo y nunca ejecuta nada del repositorio.
"""

from __future__ import annotations

import httpx

from app.repos.exceptions import RepoError
from app.repos.schemas import RepoRef

API = "https://api.github.com"


async def fetch_tarball(ref: RepoRef, token: str | None = None) -> bytes:
    url = f"{API}/repos/{ref.slug}/tarball/{ref.ref or ''}".rstrip("/")
    headers = {"accept": "application/vnd.github+json"}
    if token:
        headers["authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 404:
        raise RepoError(f"No se encontro el repositorio {ref.slug} o no es publico.")
    if response.status_code == 403:
        raise RepoError(
            "GitHub limito las peticiones. Anade un token de GitHub en Ajustes "
            "para elevar el limite."
        )
    if response.status_code >= 400:
        raise RepoError(f"GitHub respondio {response.status_code}.")
    return response.content
