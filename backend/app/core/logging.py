from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from app.config import settings


def configure() -> None:
    log_path = settings.data_dir / "lllm.log"
    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    root.addHandler(handler)
    root.addHandler(logging.StreamHandler())
