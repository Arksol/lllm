"""Parte cada archivo en fragmentos citables.

En Python se usa el arbol sintactico para no cortar una funcion por la mitad;
en los demas lenguajes se corta por bloques de lineas. La unidad resultante es
lo que despues se le muestra al modelo y lo que aparece en la cita.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

MAX_LINES = 120


@dataclass(frozen=True)
class Chunk:
    file_path: str
    start_line: int
    end_line: int
    text: str
    symbol: str | None = None

    @property
    def title(self) -> str:
        return f"{self.file_path}#L{self.start_line}-{self.end_line}"


def chunk_file(path: str, text: str) -> list[Chunk]:
    if path.endswith(".py"):
        chunks = _chunk_python(path, text)
        if chunks:
            return chunks
    return _chunk_by_lines(path, text)


def _chunk_python(path: str, text: str) -> list[Chunk]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    lines = text.splitlines()
    chunks: list[Chunk] = []
    for node in tree.body:
        if not isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            continue
        start = node.lineno
        end = getattr(node, "end_lineno", start) or start
        chunks.append(
            Chunk(
                file_path=path,
                start_line=start,
                end_line=end,
                text="\n".join(lines[start - 1 : end]),
                symbol=node.name,
            )
        )

    covered = {n for c in chunks for n in range(c.start_line, c.end_line + 1)}
    preamble = [
        (i + 1, line)
        for i, line in enumerate(lines)
        if i + 1 not in covered and line.strip()
    ]
    if preamble:
        chunks.insert(
            0,
            Chunk(
                file_path=path,
                start_line=preamble[0][0],
                end_line=preamble[-1][0],
                text="\n".join(line for _, line in preamble),
                symbol="(nivel de modulo)",
            ),
        )
    return chunks


def _chunk_by_lines(path: str, text: str) -> list[Chunk]:
    lines = text.splitlines()
    if not lines:
        return []
    chunks = []
    for start in range(0, len(lines), MAX_LINES):
        window = lines[start : start + MAX_LINES]
        if not any(line.strip() for line in window):
            continue
        chunks.append(
            Chunk(
                file_path=path,
                start_line=start + 1,
                end_line=start + len(window),
                text="\n".join(window),
            )
        )
    return chunks
