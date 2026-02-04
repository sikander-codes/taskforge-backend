import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("ACCESS_TOKEN_SECRET_KEY", "test-secret")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "5")
os.environ.setdefault("POSTGRES_USER", "u")
os.environ.setdefault("POSTGRES_PASSWORD", "p")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "test")

from app.enums import SystemRole
from app.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def fake_user():
    u = type("User", (), {})()
    u.id = uuid4()
    u.system_role = SystemRole.USER
    return u
