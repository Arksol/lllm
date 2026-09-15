from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.llm import factory
from app.llm.base import ModelInfo
from app.settings import credentials
from app.settings.models import ModelProfile
from app.settings.schemas import ProfileCreate


async def probe(provider: str, api_key: str | None, base_url: str | None) -> list[ModelInfo]:
    """Comprueba credenciales y devuelve los modelos disponibles."""
    return await factory.build_transient(provider, api_key, base_url).list_models()


def create_profile(session: Session, payload: ProfileCreate) -> ModelProfile:
    profile_id = str(uuid.uuid4())
    credential_ref = None
    if payload.api_key:
        credential_ref = f"profile:{profile_id}"
        credentials.store(credential_ref, payload.api_key)

    if payload.is_default:
        _clear_default(session)

    profile = ModelProfile(
        id=profile_id,
        name=payload.name,
        provider=payload.provider,
        model=payload.model,
        base_url=payload.base_url,
        credential_ref=credential_ref,
        is_default=payload.is_default or _is_first(session),
    )
    session.add(profile)
    session.commit()
    return profile


def set_default(session: Session, profile_id: str) -> ModelProfile:
    profile = session.get(ModelProfile, profile_id)
    if profile is None:
        raise LookupError("Perfil no encontrado.")
    _clear_default(session)
    profile.is_default = True
    session.commit()
    return profile


def delete_profile(session: Session, profile_id: str) -> None:
    profile = session.get(ModelProfile, profile_id)
    if profile is None:
        return
    credentials.delete(profile.credential_ref)
    session.delete(profile)
    session.commit()


def list_profiles(session: Session) -> list[ModelProfile]:
    return session.query(ModelProfile).order_by(ModelProfile.created_at).all()


def _clear_default(session: Session) -> None:
    session.query(ModelProfile).update({ModelProfile.is_default: False})


def _is_first(session: Session) -> bool:
    return session.query(ModelProfile).count() == 0
