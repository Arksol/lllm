from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RepoRef:
    host: str
    owner: str
    name: str
    ref: str | None = None

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.name}"

    @property
    def url(self) -> str:
        return f"https://{self.host}/{self.slug}"


@dataclass
class RepoFile:
    path: str
    text: str


@dataclass
class RepoSnapshot:
    ref: RepoRef
    root: str
    files: list[RepoFile] = field(default_factory=list)
    skipped: int = 0
