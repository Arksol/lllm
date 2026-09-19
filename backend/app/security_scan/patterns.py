"""Reglas propias, sin dependencias externas.

Sirven para que la revision funcione siempre, aunque el usuario no tenga
Semgrep, Bandit ni Trivy instalados. Cuando si los tiene, sus resultados se
suman a estos.
"""

from __future__ import annotations

import re

from app.security_scan.schemas import Severity

RULES: list[dict] = [
    {
        "id": "secreto-en-codigo",
        "pattern": re.compile(
            r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']"
        ),
        "message": "Posible credencial escrita directamente en el codigo.",
        "severity": Severity.HIGH,
        "suffixes": None,
    },
    {
        "id": "eval-dinamico",
        "pattern": re.compile(r"\b(eval|exec)\s*\("),
        "message": "Ejecucion de codigo generado en tiempo de ejecucion.",
        "severity": Severity.HIGH,
        "suffixes": {".py", ".js", ".jsx", ".ts", ".tsx"},
    },
    {
        "id": "shell-sin-aislar",
        "pattern": re.compile(r"shell\s*=\s*True|child_process\.exec\("),
        "message": "Se invoca la shell del sistema; riesgo de inyeccion de comandos.",
        "severity": Severity.HIGH,
        "suffixes": None,
    },
    {
        "id": "sql-concatenado",
        "pattern": re.compile(
            r"(?i)((select|insert|update|delete)\s+.*[\"']\s*\+|f[\"']\s*select\s)"
        ),
        "message": "Consulta SQL construida por concatenacion en vez de parametros.",
        "severity": Severity.HIGH,
        "suffixes": None,
    },
    {
        "id": "cors-abierto",
        "pattern": re.compile(
            r"allow_origins\s*=\s*\[\s*[\"']\*[\"']|origin:\s*[\"']\*[\"']"
        ),
        "message": "CORS abierto a cualquier origen.",
        "severity": Severity.MEDIUM,
        "suffixes": None,
    },
    {
        "id": "html-sin-sanitizar",
        "pattern": re.compile(r"dangerouslySetInnerHTML|\.innerHTML\s*="),
        "message": "Se inserta HTML sin sanitizar; riesgo de XSS.",
        "severity": Severity.MEDIUM,
        "suffixes": {".js", ".jsx", ".ts", ".tsx", ".html"},
    },
    {
        "id": "tls-desactivado",
        "pattern": re.compile(r"verify\s*=\s*False|rejectUnauthorized:\s*false"),
        "message": "Verificacion de certificados TLS desactivada.",
        "severity": Severity.HIGH,
        "suffixes": None,
    },
    {
        "id": "debug-en-produccion",
        "pattern": re.compile(r"(?i)debug\s*=\s*True"),
        "message": "Modo depuracion activado; puede exponer trazas internas.",
        "severity": Severity.LOW,
        "suffixes": None,
    },
]
