from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TaskPriority, TaskStatus
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import task as task_service


@pytest.fixture
def mock_db():
    db = AsyncMock(spec=AsyncSession)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def task_create_payload():
    return TaskCreate(
        title="Test task",
        description="Desc",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        assigned_to=None,
        due_date=None,
    )


async def _refresh(inst):
    if getattr(inst, "id", None) is None:
        inst.id = uuid4()
    inst.created_at = getattr(inst, "created_at", None) or datetime.now()
    inst.updated_at = getattr(inst, "updated_at", None) or datetime.now()


@pytest.mark.asyncio
async def test_create_task(mock_db, task_create_payload):
    project_id = uuid4()
    creator_id = uuid4()
    mock_db.refresh.side_effect = _refresh

    await task_service.create_task(mock_db, project_id, task_create_payload, creator_id)

    mock_db.add.assert_called_once()
    assert isinstance(mock_db.add.call_args[0][0], Task)
    assert mock_db.add.call_args[0][0].title == "Test task"
    assert mock_db.add.call_args[0][0].created_by == creator_id
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_task(mock_db):
    task = Task(
        id=uuid4(),
        project_id=uuid4(),
        title="Old",
        description=None,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        assigned_to=None,
        created_by=uuid4(),
        due_date=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        deleted_at=None,
    )
    update_data = TaskUpdate(title="New title", status=TaskStatus.DONE)

    await task_service.update_task(mock_db, task, update_data)

    assert task.title == "New title"
    assert task.status == TaskStatus.DONE
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(task)


@pytest.mark.asyncio
async def test_delete_task_soft(mock_db):
    task = Task(
        id=uuid4(),
        project_id=uuid4(),
        title="T",
        description=None,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        assigned_to=None,
        created_by=uuid4(),
        due_date=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        deleted_at=None,
    )

    await task_service.delete_task(mock_db, task)

    assert task.deleted_at is not None
    mock_db.commit.assert_awaited_once()