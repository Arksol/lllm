from __future__ import annotations

import os
import tempfile

os.environ.setdefault("LLLM_DATA_DIR", tempfile.mkdtemp(prefix="lllm-test-"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client():
    with TestClient(app, base_url="http://127.0.0.1") as test_client:
        yield test_client
