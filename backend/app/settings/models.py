"""Perfiles de modelo guardados por el usuario."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ModelProfile(Base):
    """Una combinacion guardada de proveedor + modelo + credencial.

    El usuario puede tener varios (Claude para analisis profundo, un modelo
    local para codigo privado) y cambiar entre ellos sin reconfigurar nada.
    """

    __tablename__ = "model_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    provider: Mapped[str] = mapped_column(String(60))
    model: Mapped[str] = mapped_column(String(160))
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    #: referencia al secreto en el almacen del sistema, nunca la clave en claro
    credential_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
