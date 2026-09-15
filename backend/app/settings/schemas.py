from __future__ import annotations

from pydantic import BaseModel, Field


class ProviderDescription(BaseModel):
    key: str
    label: str
    requires_api_key: bool
    supports_custom_base_url: bool


class ModelOption(BaseModel):
    id: str
    label: str
    context_window: int | None = None


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    provider: str
    model: str
    base_url: str | None = None
    api_key: str | None = None
    is_default: bool = False


class ProfileRead(BaseModel):
    id: str
    name: str
    provider: str
    model: str
    base_url: str | None
    has_api_key: bool
    is_default: bool


class ProbeRequest(BaseModel):
    provider: str
    api_key: str | None = None
    base_url: str | None = None
