"""Guarda las claves de API en el almacen de secretos del sistema operativo.

Llavero en macOS, Credential Manager en Windows, Secret Service en Linux. Si
no hay ninguno disponible, se cae a un archivo local con permisos restringidos
y se avisa al usuario en la interfaz.
"""

from __future__ import annotations

import json
import os
import stat

from app.config import settings

SERVICE = "lllm"
_FALLBACK = settings.data_dir / "credentials.json"

try:  # pragma: no cover - depende del sistema
    import keyring

    _keyring_available = keyring.get_keyring() is not None
except Exception:  # noqa: BLE001
    keyring = None  # type: ignore[assignment]
    _keyring_available = False


def keyring_available() -> bool:
    return _keyring_available


def store(ref: str, secret: str) -> None:
    if _keyring_available:
        keyring.set_password(SERVICE, ref, secret)
        return
    data = _read_fallback()
    data[ref] = secret
    _write_fallback(data)


def retrieve(ref: str | None) -> str | None:
    if not ref:
        return None
    if _keyring_available:
        return keyring.get_password(SERVICE, ref)
    return _read_fallback().get(ref)


def delete(ref: str | None) -> None:
    if not ref:
        return
    if _keyring_available:
        try:
            keyring.delete_password(SERVICE, ref)
        except Exception:  # noqa: BLE001
            pass
        return
    data = _read_fallback()
    data.pop(ref, None)
    _write_fallback(data)


def _read_fallback() -> dict[str, str]:
    if not _FALLBACK.exists():
        return {}
    return json.loads(_FALLBACK.read_text(encoding="utf-8"))


def _write_fallback(data: dict[str, str]) -> None:
    _FALLBACK.write_text(json.dumps(data), encoding="utf-8")
    if os.name != "nt":
        _FALLBACK.chmod(stat.S_IRUSR | stat.S_IWUSR)
