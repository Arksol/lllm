"""Verifica que cada cita apunte a codigo que existe de verdad.

Aunque el proveedor devuelva citas nativas, se comprueban contra los
fragmentos que enviamos. Una cita que no cuadra se descarta antes de mostrarse:
es preferible una explicacion con menos referencias que una con una falsa.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.llm.base import Citation
from app.rag.chunker import Chunk


@dataclass(frozen=True)
class VerifiedCitation:
    text: str
    file_path: str
    start_line: int
    end_line: int


def verify(citations: list[Citation], chunks: list[Chunk]) -> list[VerifiedCitation]:
    by_title = {c.title: c for c in chunks}
    by_path: dict[str, list[Chunk]] = {}
    for chunk in chunks:
        by_path.setdefault(chunk.file_path, []).append(chunk)

    verified: list[VerifiedCitation] = []
    for citation in citations:
        chunk = by_title.get(f"{citation.file_path}#L{citation.start_line}-{citation.end_line}")
        if chunk is None:
            chunk = _find_by_text(citation.text, by_path.get(citation.file_path, []))
        if chunk is None:
            continue
        if citation.text.strip() and citation.text.strip() not in chunk.text:
            continue
        verified.append(
            VerifiedCitation(
                text=citation.text.strip(),
                file_path=chunk.file_path,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
            )
        )
    return _dedupe(verified)


def _find_by_text(text: str, candidates: list[Chunk]) -> Chunk | None:
    needle = text.strip()
    if not needle:
        return None
    for chunk in candidates:
        if needle in chunk.text:
            return chunk
    return None


def _dedupe(items: list[VerifiedCitation]) -> list[VerifiedCitation]:
    seen: set[tuple[str, int, int]] = set()
    unique = []
    for item in items:
        key = (item.file_path, item.start_line, item.end_line)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique
