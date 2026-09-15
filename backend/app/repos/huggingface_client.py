"""Descarga archivos de un repositorio de Hugging Face."""

from __future__ import annotations

import httpx

from app.repos.exceptions import RepoError
from app.repos.schemas import RepoFile, RepoRef

API = "https://huggingface.co/api"


async def list_files(ref: RepoRef, token: str | None = None) -> list[str]:
    headers = {"authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.get(f"{API}/models/{ref.slug}", headers=headers)
    if response.status_code == 404:
        raise RepoError(f"No se encontro el repositorio {ref.slug} en Hugging Face.")
    if response.status_code >= 400:
        raise RepoError(f"Hugging Face respondio {response.status_code}.")
    return [item["rfilename"] for item in response.json().get("siblings", [])]


async def fetch_file(
    ref: RepoRef, path: str, token: str | None = None
) -> RepoFile | None:
    url = f"https://huggingface.co/{ref.slug}/resolve/{ref.ref or 'main'}/{path}"
    headers = {"authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
    if response.status_code >= 400:
        return None
    try:
        return RepoFile(path=path, text=response.content.decode("utf-8"))
    except UnicodeDecodeError:
        return None
