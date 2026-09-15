"""Configuracion de la aplicacion de escritorio.

Todo vive en el equipo del usuario: base de datos, claves y caches. La app no
tiene servidor propio ni recoge datos. La unica salida a internet son las
llamadas al proveedor de modelo que el usuario elija y la descarga del
repositorio que pida analizar.
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def default_data_dir() -> Path:
    """Carpeta de datos segun el sistema operativo."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif os.uname().sysname == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "lllm"


class Settings(BaseSettings):
    app_name: str = "LLLM"
    data_dir: Path = default_data_dir()

    #: la interfaz es local; solo se aceptan peticiones del propio equipo
    allowed_origins: list[str] = [
        "http://localhost:1420",
        "http://127.0.0.1:1420",
        "tauri://localhost",
    ]
    host: str = "127.0.0.1"
    port: int = 8756

    #: solo se clonan repositorios de estos dominios
    allowed_repo_hosts: list[str] = ["github.com", "huggingface.co"]
    max_repo_files: int = 800
    max_file_bytes: int = 400_000

    #: cuantos fragmentos se envian al modelo por analisis
    max_chunks_per_analysis: int = 40

    debug: bool = False

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'lllm.db'}"

    @property
    def workspace_dir(self) -> Path:
        return self.data_dir / "workspaces"

    model_config = SettingsConfigDict(env_prefix="LLLM_")


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.workspace_dir.mkdir(parents=True, exist_ok=True)
