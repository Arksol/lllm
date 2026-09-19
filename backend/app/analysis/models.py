from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    repo_url: Mapped[str] = mapped_column(String(500))
    repo_slug: Mapped[str] = mapped_column(String(300), index=True)
    host: Mapped[str] = mapped_column(String(60))
    mode: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="en_cola", index=True)
    stage: Mapped[str] = mapped_column(String(60), default="en cola")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(60), nullable=True)
    model: Mapped[str | None] = mapped_column(String(160), nullable=True)

    file_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    parent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    citations: Mapped[list[AnalysisCitation]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )
    findings: Mapped[list[AnalysisFinding]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )


class AnalysisCitation(Base):
    __tablename__ = "analysis_citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE")
    )
    text: Mapped[str] = mapped_column(Text)
    file_path: Mapped[str] = mapped_column(String(500))
    start_line: Mapped[int] = mapped_column(Integer)
    end_line: Mapped[int] = mapped_column(Integer)

    analysis: Mapped[Analysis] = relationship(back_populates="citations")


class AnalysisFinding(Base):
    __tablename__ = "analysis_findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE")
    )
    tool: Mapped[str] = mapped_column(String(40))
    rule: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20))
    file_path: Mapped[str] = mapped_column(String(500))
    line: Mapped[int] = mapped_column(Integer)

    analysis: Mapped[Analysis] = relationship(back_populates="findings")
