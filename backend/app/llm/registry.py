"""Catalogo de proveedores disponibles.

Registrar uno nuevo es una linea. La interfaz de Ajustes se construye leyendo
este registro, asi que cualquier proveedor anadido aqui aparece solo.
"""

from __future__ import annotations

from app.llm.base import LLMProvider
from app.llm.providers.anthropic_provider import AnthropicProvider
from app.llm.providers.google_provider import GoogleProvider
from app.llm.providers.ollama_provider import OllamaProvider
from app.llm.providers.openai_compatible import (
    GroqProvider,
    MistralProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
    OpenRouterProvider,
)

PROVIDERS: dict[str, type[LLMProvider]] = {
    p.key: p
    for p in (
        AnthropicProvider,
        OpenAIProvider,
        GoogleProvider,
        MistralProvider,
        GroqProvider,
        OpenRouterProvider,
        OllamaProvider,
        OpenAICompatibleProvider,
    )
}


def get_provider_class(key: str) -> type[LLMProvider]:
    try:
        return PROVIDERS[key]
    except KeyError as exc:
        raise ValueError(f"Proveedor desconocido: {key}") from exc


def describe_providers() -> list[dict]:
    """Descripcion serializable del catalogo, para la pantalla de Ajustes."""
    return [
        {
            "key": cls.key,
            "label": cls.label,
            "requires_api_key": cls.requires_api_key,
            "supports_custom_base_url": cls.supports_custom_base_url,
        }
        for cls in PROVIDERS.values()
    ]
