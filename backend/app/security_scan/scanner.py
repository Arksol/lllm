"""Revision estatica del repositorio descargado.

Nada se ejecuta: solo se lee el texto. Si el usuario tiene Semgrep, Bandit o
Trivy en el sistema, se invocan como procesos aparte y sus hallazgos se
normalizan al mismo formato.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from app.repos.schemas import RepoFile
from app.security_scan.patterns import RULES
from app.security_scan.schemas import SecurityFinding, Severity

MAX_FINDINGS = 200


def scan(files: list[RepoFile]) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    for item in files:
        suffix = Path(item.path).suffix.lower()
        for line_number, line in enumerate(item.text.splitlines(), start=1):
            if len(line) > 2000:
                continue
            for rule in RULES:
                allowed = rule["suffixes"]
                if allowed and suffix not in allowed:
                    continue
                if rule["pattern"].search(line):
                    findings.append(
                        SecurityFinding(
                            tool="lllm",
                            rule=rule["id"],
                            message=rule["message"],
                            severity=rule["severity"],
                            file_path=item.path,
                            line=line_number,
                        )
                    )
            if len(findings) >= MAX_FINDINGS:
                return findings
    return findings


def scan_with_external_tools(root: str) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    if shutil.which("semgrep"):
        findings.extend(_run_semgrep(root))
    if shutil.which("bandit"):
        findings.extend(_run_bandit(root))
    return findings


def available_tools() -> list[str]:
    return [name for name in ("semgrep", "bandit", "trivy") if shutil.which(name)]


def _run_semgrep(root: str) -> list[SecurityFinding]:
    try:
        result = subprocess.run(  # noqa: S603
            ["semgrep", "--config", "auto", "--json", "--quiet", root],
            capture_output=True, text=True, timeout=600, check=False,
        )
        payload = json.loads(result.stdout or "{}")
    except Exception:  # noqa: BLE001
        return []

    mapping = {"ERROR": Severity.HIGH, "WARNING": Severity.MEDIUM, "INFO": Severity.LOW}
    findings = []
    for item in payload.get("results", []):
        extra = item.get("extra", {})
        findings.append(
            SecurityFinding(
                tool="semgrep",
                rule=item.get("check_id", ""),
                message=extra.get("message", ""),
                severity=mapping.get(extra.get("severity", "INFO"), Severity.LOW),
                file_path=_relative(item.get("path", ""), root),
                line=item.get("start", {}).get("line", 0),
            )
        )
    return findings


def _run_bandit(root: str) -> list[SecurityFinding]:
    try:
        result = subprocess.run(  # noqa: S603
            ["bandit", "-r", root, "-f", "json", "-q"],
            capture_output=True, text=True, timeout=600, check=False,
        )
        payload = json.loads(result.stdout or "{}")
    except Exception:  # noqa: BLE001
        return []

    mapping = {"HIGH": Severity.HIGH, "MEDIUM": Severity.MEDIUM, "LOW": Severity.LOW}
    return [
        SecurityFinding(
            tool="bandit",
            rule=item.get("test_id", ""),
            message=item.get("issue_text", ""),
            severity=mapping.get(item.get("issue_severity", "LOW"), Severity.LOW),
            file_path=_relative(item.get("filename", ""), root),
            line=item.get("line_number", 0),
        )
        for item in payload.get("results", [])
    ]


def _relative(path: str, root: str) -> str:
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        return path
