"""Orquesta el pipeline completo de un analisis.

Es el unico modulo que conoce a los demas dominios. Los dominios entre si no
se conocen: eso es lo que permite sustituir cualquiera de ellos sin tocar el
resto.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.analysis.models import Analysis, AnalysisCitation, AnalysisFinding
from app.analysis.schemas import AnalysisCreate
from app.config import settings
from app.database import SessionLocal
from app.llm import factory
from app.llm.base import Message, ProviderError
from app.llm.prompts import analysis as prompts
from app.rag import citations as citation_service
from app.rag.chunker import Chunk, chunk_file
from app.rag.models import CodeChunk
from app.rag.retrieval import BM25Index, select_overview
from app.repos import ingest
from app.repos.exceptions import RepoError
from app.repos.validators import parse_repo_url
from app.security_scan import scanner


def create(session: Session, payload: AnalysisCreate) -> Analysis:
    """Registra el analisis. La ejecucion ocurre despues, en segundo plano."""
    ref = parse_repo_url(payload.repo_url)
    factory.resolve_active(session, payload.profile_id)  # falla pronto si no hay modelo

    record = Analysis(
        id=str(uuid.uuid4()),
        repo_url=ref.url,
        repo_slug=ref.slug,
        host=ref.host,
        mode=payload.mode,
        status="en_cola",
        stage="en cola",
    )
    session.add(record)
    session.commit()
    return record


def regenerate(session: Session, analysis_id: str, mode: str | None) -> Analysis:
    previous = session.get(Analysis, analysis_id)
    if previous is None:
        raise LookupError("Analisis no encontrado.")

    record = Analysis(
        id=str(uuid.uuid4()),
        repo_url=previous.repo_url,
        repo_slug=previous.repo_slug,
        host=previous.host,
        mode=mode or previous.mode,
        status="en_cola",
        stage="en cola",
        parent_id=previous.id,
    )
    session.add(record)
    session.commit()
    return record


async def run(analysis_id: str, profile_id: str | None = None) -> None:
    """Ejecuta el pipeline. Abre su propia sesion: corre fuera de la peticion."""
    session = SessionLocal()
    workspace: str | None = None
    try:
        record = session.get(Analysis, analysis_id)
        if record is None:
            return

        profile = factory.resolve_active(session, profile_id)
        provider = factory.build_from_profile(profile)
        record.provider, record.model = profile.provider, profile.model

        _advance(session, record, "descargando repositorio")
        ref = parse_repo_url(record.repo_url)
        snapshot = await ingest.snapshot(ref)
        workspace = snapshot.root
        record.file_count = len(snapshot.files)

        _advance(session, record, "construyendo fragmentos")
        chunks: list[Chunk] = []
        for item in snapshot.files:
            chunks.extend(chunk_file(item.path, item.text))
        record.chunk_count = len(chunks)
        _persist_chunks(session, record.id, chunks)

        _advance(session, record, "revisando seguridad")
        findings = scanner.scan(snapshot.files)
        findings.extend(scanner.scan_with_external_tools(snapshot.root))
        _persist_findings(session, record.id, findings)

        _advance(session, record, "generando explicacion")
        selected = select_overview(chunks, settings.max_chunks_per_analysis)
        completion = await provider.complete(
            model=profile.model,
            system=prompts.system_prompt(record.mode),
            messages=[
                Message(
                    role="user",
                    content=prompts.user_prompt(
                        record.repo_url, record.file_count, record.mode
                    ),
                )
            ],
            documents=[_as_document(c) for c in selected],
        )

        record.explanation = completion.text
        _persist_citations(
            session, record.id, citation_service.verify(completion.citations, selected)
        )
        record.status = "listo"
        record.stage = "listo"
        record.finished_at = datetime.utcnow()
        session.commit()

    except (RepoError, ProviderError, factory.NoModelConfigured) as exc:
        _fail(session, analysis_id, str(exc))
    except Exception as exc:  # noqa: BLE001
        _fail(session, analysis_id, f"Fallo inesperado: {exc}")
    finally:
        ingest.discard(workspace)
        session.close()


async def ask(session: Session, analysis_id: str, question: str) -> tuple[str, list]:
    """Vuelve a preguntar sobre un analisis ya hecho, sin redescargar nada."""
    record = session.get(Analysis, analysis_id)
    if record is None:
        raise LookupError("Analisis no encontrado.")

    stored = (
        session.query(CodeChunk).filter(CodeChunk.analysis_id == analysis_id).all()
    )
    if not stored:
        raise LookupError("Este analisis ya no conserva los fragmentos.")

    chunks = [
        Chunk(
            file_path=c.file_path,
            start_line=c.start_line,
            end_line=c.end_line,
            text=c.text,
            symbol=c.symbol,
        )
        for c in stored
    ]
    selected = BM25Index(chunks).search(question, settings.max_chunks_per_analysis)

    profile = factory.resolve_active(session)
    provider = factory.build_from_profile(profile)
    completion = await provider.complete(
        model=profile.model,
        system=prompts.system_prompt(record.mode),
        messages=[Message(role="user", content=prompts.followup_prompt(question))],
        documents=[_as_document(c) for c in selected],
    )
    return completion.text, citation_service.verify(completion.citations, selected)


def _as_document(chunk: Chunk) -> dict:
    return {
        "title": chunk.title,
        "text": chunk.text,
        "context": f"Simbolo: {chunk.symbol}" if chunk.symbol else "",
    }


def _advance(session: Session, record: Analysis, stage: str) -> None:
    record.status = "procesando"
    record.stage = stage
    session.commit()


def _fail(session: Session, analysis_id: str, message: str) -> None:
    record = session.get(Analysis, analysis_id)
    if record is None:
        return
    record.status = "error"
    record.stage = "error"
    record.error = message
    record.finished_at = datetime.utcnow()
    session.commit()


def _persist_chunks(session: Session, analysis_id: str, chunks: list[Chunk]) -> None:
    session.bulk_save_objects(
        [
            CodeChunk(
                analysis_id=analysis_id,
                file_path=c.file_path,
                start_line=c.start_line,
                end_line=c.end_line,
                symbol=c.symbol,
                text=c.text,
            )
            for c in chunks
        ]
    )
    session.commit()


def _persist_findings(session: Session, analysis_id: str, findings: list) -> None:
    session.bulk_save_objects(
        [
            AnalysisFinding(
                analysis_id=analysis_id,
                tool=f.tool,
                rule=f.rule,
                message=f.message,
                severity=f.severity.value,
                file_path=f.file_path,
                line=f.line,
            )
            for f in findings
        ]
    )
    session.commit()


def _persist_citations(session: Session, analysis_id: str, citations: list) -> None:
    session.bulk_save_objects(
        [
            AnalysisCitation(
                analysis_id=analysis_id,
                text=c.text,
                file_path=c.file_path,
                start_line=c.start_line,
                end_line=c.end_line,
            )
            for c in citations
        ]
    )
    session.commit()
