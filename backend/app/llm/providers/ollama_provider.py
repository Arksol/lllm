"""Proveedor Ollama: modelos que corren en la maquina del propio usuario.

No pide clave y no sale a internet. Es la opcion para analizar codigo privado
sin que salga del equipo.
"""

from __future__ import annotations

import httpx

from app.llm.base import (
    Completion,
    LLMProvider,
    Message,
    ModelInfo,
    ProviderError,
)
from app.llm.providers.openai_compatible import _with_documents


class OllamaProvider(LLMProvider):
    key = "ollama"
    label = "Ollama (local)"
    requires_api_key = False
    supports_custom_base_url = True

    DEFAULT_BASE_URL = "http://localhost:11434"

    @property
    def _url(self) -> str:
        return (self.base_url or self.DEFAULT_BASE_URL).rstrip("/")

    async def list_models(self) -> list[ModelInfo]:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(f"{self._url}/api/tags")
        except httpx.HTTPError as exc:
            raise ProviderError(
                f"No se pudo conectar con Ollama en {self._url}. "
                "Comprueba que este en ejecucion."
            ) from exc
        if response.status_code >= 400:
            raise ProviderError(response.text)
        return [
            ModelInfo(id=item["name"], label=item["name"])
            for item in response.json().get("models", [])
        ]

    async def complete(
        self,
        *,
        model: str,
        system: str,
        messages: list[Message],
        documents: list[dict] | None = None,
        max_tokens: int = 4096,
    ) -> Completion:
        payload = {
            "model": model,
            "stream": False,
            "options": {"num_predict": max_tokens},
            "messages": [
                {"role": "system", "content": system},
                *({"role": m.role, "content": m.content} for m in messages[:-1]),
                {
                    "role": "user",
                    "content": _with_documents(messages[-1].content, documents),
                },
            ],
        }
        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(f"{self._url}/api/chat", json=payload)
        if response.status_code >= 400:
            raise ProviderError(response.text)

        data = response.json()
        return Completion(
            text=data.get("message", {}).get("content", ""),
            model=data.get("model", model),
            input_tokens=data.get("prompt_eval_count"),
            output_tokens=data.get("eval_count"),
        )
