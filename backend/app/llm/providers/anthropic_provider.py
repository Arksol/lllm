"""Proveedor Anthropic (Claude).

Usa la API de mensajes y, cuando se le pasan documentos, activa Citations para
que cada afirmacion quede anclada a un fragmento real del repositorio.
"""

from __future__ import annotations

import httpx

from app.llm.base import (
    Citation,
    Completion,
    LLMProvider,
    Message,
    ModelInfo,
    ProviderError,
)

API_VERSION = "2023-06-01"


class AnthropicProvider(LLMProvider):
    key = "anthropic"
    label = "Anthropic (Claude)"
    requires_api_key = True
    supports_custom_base_url = False

    DEFAULT_BASE_URL = "https://api.anthropic.com"

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ProviderError("Falta la clave de API de Anthropic.")
        return {
            "x-api-key": self.api_key,
            "anthropic-version": API_VERSION,
            "content-type": "application/json",
        }

    async def list_models(self) -> list[ModelInfo]:
        url = f"{self.base_url or self.DEFAULT_BASE_URL}/v1/models"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self._headers())
        if response.status_code >= 400:
            raise ProviderError(_message_from(response))
        return [
            ModelInfo(id=item["id"], label=item.get("display_name", item["id"]))
            for item in response.json().get("data", [])
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
        content: list[dict] = []
        for document in documents or []:
            content.append(_as_document_block(document))
        content.append({"type": "text", "text": messages[-1].content})

        history = [
            {"role": m.role, "content": m.content} for m in messages[:-1]
        ]
        history.append({"role": "user", "content": content})

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": history,
        }

        url = f"{self.base_url or self.DEFAULT_BASE_URL}/v1/messages"
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(url, headers=self._headers(), json=payload)
        if response.status_code >= 400:
            raise ProviderError(_message_from(response))

        data = response.json()
        text_parts: list[str] = []
        citations: list[Citation] = []
        for block in data.get("content", []):
            if block.get("type") != "text":
                continue
            text_parts.append(block.get("text", ""))
            for raw in block.get("citations") or []:
                citations.append(_as_citation(raw))

        usage = data.get("usage", {})
        return Completion(
            text="".join(text_parts),
            citations=citations,
            model=data.get("model", model),
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
        )


def _as_document_block(document: dict) -> dict:
    """Un fragmento de codigo como documento citable.

    Se usa `custom content`: cada bloque que enviamos es la unidad citable
    minima, asi la cita apunta a la funcion exacta y no a media linea.
    """
    return {
        "type": "document",
        "source": {
            "type": "content",
            "content": [{"type": "text", "text": document["text"]}],
        },
        "title": document["title"],
        "context": document.get("context", ""),
        "citations": {"enabled": True},
    }


def _as_citation(raw: dict) -> Citation:
    title = raw.get("document_title", "")
    file_path, _, line_range = title.partition("#L")
    start, _, end = line_range.partition("-")
    return Citation(
        text=raw.get("cited_text", ""),
        file_path=file_path or title,
        start_line=int(start) if start.isdigit() else 0,
        end_line=int(end) if end.isdigit() else 0,
    )


def _message_from(response: httpx.Response) -> str:
    try:
        return response.json().get("error", {}).get("message", response.text)
    except Exception:  # noqa: BLE001
        return response.text
