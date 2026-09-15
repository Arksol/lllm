"""Selecciona que fragmentos ve el modelo.

Se usa BM25 en memoria: no depende de un servicio de embeddings, funciona sin
conexion y hace que la app sirva igual con un modelo local que con uno remoto.
La puntuacion se complementa con senales estructurales (archivos raiz,
configuracion, puntos de entrada) porque son los que explican un proyecto.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from app.rag.chunker import Chunk

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}")

ENTRY_POINTS = {
    "main.py", "app.py", "index.js", "index.ts", "main.js", "main.ts",
    "app.jsx", "app.tsx", "server.js", "mod.rs", "main.rs", "main.go",
}
CONFIG_NAMES = {
    "package.json", "pyproject.toml", "requirements.txt", "cargo.toml",
    "go.mod", "dockerfile", "docker-compose.yml", "readme.md",
}


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text)]


class BM25Index:
    K1 = 1.5
    B = 0.75

    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.docs = [Counter(tokenize(c.text)) for c in chunks]
        self.lengths = [sum(d.values()) or 1 for d in self.docs]
        self.avg_length = sum(self.lengths) / len(self.lengths) if self.lengths else 1
        self.df: Counter[str] = Counter()
        for doc in self.docs:
            self.df.update(doc.keys())

    def score(self, query: str, index: int) -> float:
        total = 0.0
        doc, length = self.docs[index], self.lengths[index]
        n = len(self.docs)
        for term in tokenize(query):
            freq = doc.get(term)
            if not freq:
                continue
            idf = math.log(1 + (n - self.df[term] + 0.5) / (self.df[term] + 0.5))
            denominator = freq + self.K1 * (1 - self.B + self.B * length / self.avg_length)
            total += idf * (freq * (self.K1 + 1)) / denominator
        return total

    def search(self, query: str, limit: int) -> list[Chunk]:
        ranked = sorted(
            range(len(self.chunks)),
            key=lambda i: self.score(query, i) + structural_bonus(self.chunks[i]),
            reverse=True,
        )
        return [self.chunks[i] for i in ranked[:limit]]


def structural_bonus(chunk: Chunk) -> float:
    """Un README o un punto de entrada explican mas que un archivo cualquiera."""
    name = Path(chunk.file_path).name.lower()
    depth = len(Path(chunk.file_path).parts) - 1
    bonus = 0.0
    if name in CONFIG_NAMES:
        bonus += 3.0
    if name in ENTRY_POINTS:
        bonus += 2.5
    bonus += max(0.0, 1.5 - depth * 0.3)
    return bonus


def select_overview(chunks: list[Chunk], limit: int) -> list[Chunk]:
    """Seleccion inicial para explicar un proyecto que aun no se conoce."""
    ordered = sorted(chunks, key=structural_bonus, reverse=True)
    picked: list[Chunk] = []
    seen_files: set[str] = set()
    for chunk in ordered:
        if len(picked) >= limit:
            break
        # se favorece la variedad de archivos antes que agotar uno solo
        if chunk.file_path in seen_files and len(seen_files) < limit // 2:
            continue
        seen_files.add(chunk.file_path)
        picked.append(chunk)
    return picked
