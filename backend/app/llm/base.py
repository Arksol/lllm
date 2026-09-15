"""Contrato unico que toda la aplicacion conoce sobre un modelo de lenguaje.

Ningun dominio (analysis, rag, security_scan) importa un SDK de proveedor
directamente. Todos hablan con esta interfaz. Anadir un proveedor nuevo es
crear un archivo en providers/ y registrarlo: nada mas del codigo cambia.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass(frozen=True)
class Message:
    role: str  # "user" | "assistant"
    content: str


@dataclass(frozen=True)
class ModelInfo:
    id: str
    label: str
    context_window: int | None = None


@dataclass(frozen=True)
class Citation:
    """Una cita anclada a un fragmento real del repositorio."""

    text: str
    file_path: str
    start_line: int
    end_line: int


@dataclass
class Completion:
    text: str
    citations: list[Citation] = field(default_factory=list)
    model: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None


class ProviderError(Exception):
    """Fallo atribuible al proveedor (credenciales, cuota, red)."""


class LLMProvider(ABC):
    """Interfaz que implementan todos los proveedores."""

    #: identificador estable usado en configuracion y base de datos
    key: str = ""
    #: nombre mostrado en la interfaz
    label: str = ""
    #: si False, el proveedor no pide clave (p. ej. un modelo local)
    requires_api_key: bool = True
    #: si True, el usuario puede escribir su propia URL base
    supports_custom_base_url: bool = False

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """Modelos disponibles para las credenciales dadas."""

    @abstractmethod
    async def complete(
        self,
        *,
        model: str,
        system: str,
        messages: list[Message],
        documents: list[dict] | None = None,
        max_tokens: int = 4096,
    ) -> Completion:
        """Genera una respuesta completa."""

    async def stream(
        self,
        *,
        model: str,
        system: str,
        messages: list[Message],
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Genera la respuesta por fragmentos. Por defecto cae a complete()."""
        result = await self.complete(
            model=model, system=system, messages=messages, max_tokens=max_tokens
        )
        yield result.text

    async def check(self) -> bool:
        """Comprueba que las credenciales sirven. Usado por Ajustes."""
        try:
            await self.list_models()
            return True
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(str(exc)) from exc
