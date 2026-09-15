from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Mode = Literal["junior", "senior"]


class AnalysisCreate(BaseModel):
    repo_url: str = Field(min_length=3, max_length=500)
    mode: Mode = "junior"
    profile_id: str | None = None


class CitationRead(BaseModel):
    text: str
    file_path: str
    start_line: int
    end_line: int


class FindingRead(BaseModel):
    tool: str
    rule: str
    message: str
    severity: str
    file_path: str
    line: int


class AnalysisRead(BaseModel):
    id: str
    repo_url: str
    repo_slug: str
    mode: str
    status: str
    stage: str
    error: str | None = None
    explanation: str | None = None
    provider: str | None = None
    model: str | None = None
    file_count: int
    chunk_count: int
    parent_id: str | None = None
    created_at: datetime
    finished_at: datetime | None = None
    citations: list[CitationRead] = []
    findings: list[FindingRead] = []


class AnalysisSummary(BaseModel):
    id: str
    repo_slug: str
    repo_url: str
    mode: str
    status: str
    created_at: datetime


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class QuestionResponse(BaseModel):
    answer: str
    citations: list[CitationRead] = []
