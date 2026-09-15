from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.analysis import service
from app.analysis.models import Analysis
from app.analysis.schemas import (
    AnalysisCreate,
    AnalysisRead,
    AnalysisSummary,
    CitationRead,
    FindingRead,
    QuestionRequest,
    QuestionResponse,
)
from app.api.deps import db_session
from app.llm.base import ProviderError
from app.llm.factory import NoModelConfigured
from app.repos.exceptions import RepoError

router = APIRouter(prefix="/analysis", tags=["analisis"])


@router.post("", response_model=AnalysisRead, status_code=status.HTTP_202_ACCEPTED)
def create_analysis(
    payload: AnalysisCreate,
    background: BackgroundTasks,
    session: Session = Depends(db_session),
) -> AnalysisRead:
    try:
        record = service.create(session, payload)
    except RepoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except NoModelConfigured as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc

    background.add_task(service.run, record.id, payload.profile_id)
    return _read(record)


@router.get("/history", response_model=list[AnalysisSummary])
def history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(db_session),
) -> list[AnalysisSummary]:
    records = (
        session.query(Analysis)
        .order_by(Analysis.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [
        AnalysisSummary(
            id=r.id,
            repo_slug=r.repo_slug,
            repo_url=r.repo_url,
            mode=r.mode,
            status=r.status,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/{analysis_id}", response_model=AnalysisRead)
def get_analysis(analysis_id: str, session: Session = Depends(db_session)) -> AnalysisRead:
    record = session.get(Analysis, analysis_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Analisis no encontrado.")
    return _read(record)


@router.post(
    "/{analysis_id}/regenerate",
    response_model=AnalysisRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def regenerate(
    analysis_id: str,
    background: BackgroundTasks,
    mode: str | None = None,
    session: Session = Depends(db_session),
) -> AnalysisRead:
    try:
        record = service.regenerate(session, analysis_id, mode)
    except LookupError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    background.add_task(service.run, record.id, None)
    return _read(record)


@router.post("/{analysis_id}/ask", response_model=QuestionResponse)
async def ask(
    analysis_id: str,
    payload: QuestionRequest,
    session: Session = Depends(db_session),
) -> QuestionResponse:
    try:
        answer, citations = await service.ask(session, analysis_id, payload.question)
    except LookupError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except (ProviderError, NoModelConfigured) as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return QuestionResponse(
        answer=answer,
        citations=[CitationRead(**vars(c)) for c in citations],
    )


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: str, session: Session = Depends(db_session)) -> None:
    record = session.get(Analysis, analysis_id)
    if record is not None:
        session.delete(record)
        session.commit()


def _read(record: Analysis) -> AnalysisRead:
    return AnalysisRead(
        id=record.id,
        repo_url=record.repo_url,
        repo_slug=record.repo_slug,
        mode=record.mode,
        status=record.status,
        stage=record.stage,
        error=record.error,
        explanation=record.explanation,
        provider=record.provider,
        model=record.model,
        file_count=record.file_count,
        chunk_count=record.chunk_count,
        parent_id=record.parent_id,
        created_at=record.created_at,
        finished_at=record.finished_at,
        citations=[
            CitationRead(
                text=c.text,
                file_path=c.file_path,
                start_line=c.start_line,
                end_line=c.end_line,
            )
            for c in record.citations
        ],
        findings=[
            FindingRead(
                tool=f.tool,
                rule=f.rule,
                message=f.message,
                severity=f.severity,
                file_path=f.file_path,
                line=f.line,
            )
            for f in record.findings
        ],
    )
