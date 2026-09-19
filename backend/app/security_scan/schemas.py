from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    INFO = "info"
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"


@dataclass(frozen=True)
class SecurityFinding:
    tool: str
    rule: str
    message: str
    severity: Severity
    file_path: str
    line: int
