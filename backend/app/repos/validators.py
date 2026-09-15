"""Valida la URL antes de tocar la red.

Solo se aceptan dominios de la lista permitida. Esto evita que la aplicacion
se convierta en un puente para alcanzar direcciones internas de la red del
usuario a partir de una URL manipulada.
"""

from __future__ import annotations

from urllib.parse import urlparse

from app.config import settings
from app.repos.exceptions import RepoError, UnsupportedHost
from app.repos.schemas import RepoRef


def parse_repo_url(raw: str) -> RepoRef:
    candidate = raw.strip()
    if not candidate:
        raise RepoError("Escribe la URL de un repositorio.")
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme != "https":
        raise RepoError("Solo se aceptan URL https.")

    host = (parsed.hostname or "").lower().removeprefix("www.")
    if host not in settings.allowed_repo_hosts:
        raise UnsupportedHost(
            f"Dominio no permitido: {host or 'desconocido'}. "
            f"Permitidos: {', '.join(settings.allowed_repo_hosts)}."
        )

    parts = [p for p in parsed.path.split("/") if p]
    if host == "huggingface.co" and parts and parts[0] in {"datasets", "spaces"}:
        parts = parts[1:]
    if len(parts) < 2:
        raise RepoError("La URL debe incluir propietario y nombre del repositorio.")

    owner, name = parts[0], parts[1].removesuffix(".git")
    ref = parts[3] if len(parts) > 3 and parts[2] in {"tree", "blob"} else None
    return RepoRef(host=host, owner=owner, name=name, ref=ref)
