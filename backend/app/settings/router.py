from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.llm.base import ProviderError
from app.llm.registry import describe_providers
from app.settings import credentials, service
from app.settings.schemas import (
    ModelOption,
    ProbeRequest,
    ProfileCreate,
    ProfileRead,
    ProviderDescription,
)

router = APIRouter(prefix="/settings", tags=["ajustes"])


@router.get("/providers", response_model=list[ProviderDescription])
def providers() -> list[dict]:
    return describe_providers()


@router.get("/storage")
def storage() -> dict:
    """Indica si las claves van al almacen del sistema o a un archivo local."""
    return {
        "keyring_available": credentials.keyring_available(),
        "detail": (
            "Las claves se guardan en el almacen de secretos del sistema."
            if credentials.keyring_available()
            else "No hay almacen de secretos disponible; las claves se guardan "
            "en un archivo local con permisos restringidos."
        ),
    }


@router.post("/probe", response_model=list[ModelOption])
async def probe(payload: ProbeRequest) -> list[ModelOption]:
    try:
        models = await service.probe(payload.provider, payload.api_key, payload.base_url)
    except ProviderError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return [ModelOption(**vars(m)) for m in models]


@router.get("/profiles", response_model=list[ProfileRead])
def profiles(session: Session = Depends(db_session)) -> list[ProfileRead]:
    return [_read(p) for p in service.list_profiles(session)]


@router.post("/profiles", response_model=ProfileRead, status_code=201)
def create_profile(
    payload: ProfileCreate, session: Session = Depends(db_session)
) -> ProfileRead:
    return _read(service.create_profile(session, payload))


@router.post("/profiles/{profile_id}/default", response_model=ProfileRead)
def set_default(profile_id: str, session: Session = Depends(db_session)) -> ProfileRead:
    try:
        return _read(service.set_default(session, profile_id))
    except LookupError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.delete("/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: str, session: Session = Depends(db_session)) -> None:
    service.delete_profile(session, profile_id)


def _read(profile) -> ProfileRead:
    return ProfileRead(
        id=profile.id,
        name=profile.name,
        provider=profile.provider,
        model=profile.model,
        base_url=profile.base_url,
        has_api_key=bool(profile.credential_ref),
        is_default=profile.is_default,
    )
