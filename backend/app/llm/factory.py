"""Construye un proveedor listo para usar a partir de un perfil guardado."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.llm.base import LLMProvider
from app.llm.registry import get_provider_class
from app.settings import credentials
from app.settings.models import ModelProfile


class NoModelConfigured(Exception):
    """Aun no hay ningun perfil de modelo configurado."""


def build_from_profile(profile: ModelProfile) -> LLMProvider:
    provider_cls = get_provider_class(profile.provider)
    return provider_cls(
        api_key=credentials.retrieve(profile.credential_ref),
        base_url=profile.base_url,
    )


def build_transient(
    provider: str, api_key: str | None, base_url: str | None
) -> LLMProvider:
    """Proveedor de un solo uso, para probar credenciales antes de guardarlas."""
    return get_provider_class(provider)(api_key=api_key, base_url=base_url)


def resolve_active(session: Session, profile_id: str | None = None) -> ModelProfile:
    query = session.query(ModelProfile)
    profile = (
        query.filter(ModelProfile.id == profile_id).one_or_none()
        if profile_id
        else query.filter(ModelProfile.is_default.is_(True)).one_or_none()
        or query.order_by(ModelProfile.created_at).first()
    )
    if profile is None:
        raise NoModelConfigured(
            "Configura un modelo en Ajustes antes de analizar un repositorio."
        )
    return profile
