"""Proveedor Google (Gemini) mediante la API generativeLanguage."""

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


class GoogleProvider(LLMProvider):
    key = "google"
    label = "Google (Gemini)"
    requires_api_key = True
    supports_custom_base_url = False

    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    @property
    def _url(self) -> str:
        return (self.base_url or self.DEFAULT_BASE_URL).rstrip("/")

    def _params(self) -> dict[str, str]:
        if not self.api_key:
            raise ProviderError("Falta la clave de API de Google.")
        return {"key": self.api_key}

    async def list_models(self) -> list[ModelInfo]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self._url}/models", params=self._params())
        if response.status_code >= 400:
            raise ProviderError(response.text)
        models = []
        for item in response.json().get("models", []):
            if "generateContent" not in item.get("supportedGenerationMethods", []):
                continue
            name = item["name"].removeprefix("models/")
            models.append(
                ModelInfo(
                    id=name,
                    label=item.get("displayName", name),
                    context_window=item.get("inputTokenLimit"),
                )
            )
        return models

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
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [
                {
                    "role": "user" if m.role == "user" else "model",
                    "parts": [{"text": m.content}],
                }
                for m in messages[:-1]
            ]
            + [
                {
                    "role": "user",
                    "parts": [{"text": _with_documents(messages[-1].content, documents)}],
                }
            ],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{self._url}/models/{model}:generateContent",
                params=self._params(),
                json=payload,
            )
        if response.status_code >= 400:
            raise ProviderError(response.text)

        data = response.json()
        candidate = (data.get("candidates") or [{}])[0]
        parts = candidate.get("content", {}).get("parts", [])
        usage = data.get("usageMetadata", {})
        return Completion(
            text="".join(p.get("text", "") for p in parts),
            model=model,
            input_tokens=usage.get("promptTokenCount"),
            output_tokens=usage.get("candidatesTokenCount"),
        )
