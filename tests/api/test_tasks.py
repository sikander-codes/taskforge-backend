"""API tests for task endpoints (mocked auth and services)."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status

from app.enums import ProjectRole, TaskPriority, TaskStatus


@pytest.fixture
def app_with_overrides(app, fake_user):
    """Override get_db and get_current_user so endpoints run without real DB."""
    from app.api.dependencies.auth import get_current_user
    from app.core.database import get_db

    async def override_get_db():
        yield None

    async def override_current_user():
        return fake_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client_override(app_with_overrides):
    from fastapi.testclient import TestClient
    return TestClient(app_with_overrides)


def test_create_task_201(client_override, fake_user):
    project_id = uuid4()
    task_id = uuid4()
    now = datetime.now()
    fake_task = type("Task", (), {
        "id": task_id, "project_id": project_id, "title": "New",
        "description": None, "status": TaskStatus.TODO, "priority": TaskPriority.MEDIUM,
        "assigned_to": None, "created_by": fake_user.id, "due_date": None,
        "created_at": now, "updated_at": now, "deleted_at": None,
    })()

    with (
        patch("app.api.v1.tasks.project_service.get_membership", new_callable=AsyncMock, return_value=MagicMock(role=ProjectRole.MEMBER)),
        patch("app.api.v1.tasks.project_service.get_project", new_callable=AsyncMock, return_value=object()),
        patch("app.api.v1.tasks.task_service.create_task", new_callable=AsyncMock, return_value=fake_task),
    ):
        resp = client_override.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "New", "description": None},
            headers={"Authorization": "Bearer any"},
        )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["title"] == "New"
    assert resp.json()["id"] == str(task_id)


def test_create_task_404_project_not_found(client_override, fake_user):
    project_id = uuid4()
    with (
        patch("app.api.v1.tasks.project_service.get_membership", new_callable=AsyncMock, return_value=MagicMock(role=ProjectRole.MEMBER)),
        patch("app.api.v1.tasks.project_service.get_project", new_callable=AsyncMock, return_value=None),
    ):
        resp = client_override.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "New"},
            headers={"Authorization": "Bearer any"},
        )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp.json()["detail"].lower()


def test_get_task_404(client_override, fake_user):
    project_id = uuid4()
    task_id = uuid4()
    with (
        patch("app.api.v1.tasks.project_service.get_membership", new_callable=AsyncMock, return_value=MagicMock(role=ProjectRole.MEMBER)),
        patch("app.api.v1.tasks.task_service.get_task", new_callable=AsyncMock, return_value=None),
    ):
        resp = client_override.get(
            f"/api/v1/projects/{project_id}/tasks/{task_id}",
            headers={"Authorization": "Bearer any"},
        )
    assert resp.status_code == status.HTTP_404_NOT_FOUND