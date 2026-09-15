"""SQLite local. Una aplicacion de escritorio no debe pedirle al usuario que
instale y administre un servidor de base de datos."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.debug,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_all() -> None:
    from app.analysis import models as analysis_models  # noqa: F401
    from app.rag import models as rag_models  # noqa: F401
    from app.settings import models as settings_models  # noqa: F401

    Base.metadata.create_all(engine)
