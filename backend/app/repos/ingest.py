"""Convierte una URL en una instantanea de archivos de texto en disco.

Nada de lo descargado se ejecuta. Solo se leen archivos de texto con
extensiones conocidas, con limite de cantidad y de tamano.
"""

from __future__ import annotations

import io
import shutil
import tarfile
import uuid
from pathlib import Path

from app.config import settings
from app.repos import github_client, huggingface_client
from app.repos.exceptions import RepoError
from app.repos.schemas import RepoFile, RepoRef, RepoSnapshot

TEXT_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".rs", ".go", ".java", ".kt", ".rb",
    ".php", ".c", ".h", ".cpp", ".hpp", ".cs", ".swift", ".sql", ".sh",
    ".html", ".css", ".scss", ".vue", ".svelte", ".md", ".rst", ".txt",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env.example",
    ".dockerfile", ".gradle",
}
SKIP_PARTS = {
    "node_modules", ".git", "dist", "build", "vendor", "__pycache__",
    ".venv", "venv", "target", ".next", ".cache", "site-packages",
}


async def snapshot(ref: RepoRef, token: str | None = None) -> RepoSnapshot:
    workspace = settings.workspace_dir / f"{ref.owner}-{ref.name}-{uuid.uuid4().hex[:8]}"
    workspace.mkdir(parents=True, exist_ok=True)
    try:
        if ref.host == "github.com":
            files, skipped = await _from_github(ref, token)
        else:
            files, skipped = await _from_huggingface(ref, token)
    except Exception:
        shutil.rmtree(workspace, ignore_errors=True)
        raise

    if not files:
        shutil.rmtree(workspace, ignore_errors=True)
        raise RepoError("El repositorio no contiene archivos de texto analizables.")

    return RepoSnapshot(ref=ref, root=str(workspace), files=files, skipped=skipped)


def discard(root: str | None) -> None:
    if root:
        shutil.rmtree(root, ignore_errors=True)


async def _from_github(ref: RepoRef, token: str | None) -> tuple[list[RepoFile], int]:
    raw = await github_client.fetch_tarball(ref, token)
    files: list[RepoFile] = []
    skipped = 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for member in archive:
            if not member.isfile():
                continue
            path = _strip_root(member.name)
            if not _is_wanted(path):
                skipped += 1
                continue
            if member.size > settings.max_file_bytes:
                skipped += 1
                continue
            if len(files) >= settings.max_repo_files:
                skipped += 1
                continue
            handle = archive.extractfile(member)
            if handle is None:
                continue
            try:
                files.append(RepoFile(path=path, text=handle.read().decode("utf-8")))
            except UnicodeDecodeError:
                skipped += 1
    return files, skipped


async def _from_huggingface(ref: RepoRef, token: str | None) -> tuple[list[RepoFile], int]:
    paths = await huggingface_client.list_files(ref, token)
    files: list[RepoFile] = []
    skipped = 0
    for path in paths:
        if not _is_wanted(path):
            skipped += 1
            continue
        if len(files) >= settings.max_repo_files:
            skipped += 1
            continue
        item = await huggingface_client.fetch_file(ref, path, token)
        if item is None:
            skipped += 1
            continue
        files.append(item)
    return files, skipped


def _strip_root(name: str) -> str:
    """El tarball de GitHub envuelve todo en una carpeta con el hash."""
    parts = name.split("/", 1)
    return parts[1] if len(parts) == 2 else name


def _is_wanted(path: str) -> bool:
    p = Path(path)
    if any(part in SKIP_PARTS for part in p.parts):
        return False
    if p.name.lower() in {"dockerfile", "makefile", "license"}:
        return True
    return p.suffix.lower() in TEXT_SUFFIXES
