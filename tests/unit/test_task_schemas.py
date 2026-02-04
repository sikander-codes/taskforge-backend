import pytest
from pydantic import ValidationError

from app.enums import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def test_task_create_valid():
    data = {"title": "A task", "description": "Optional"}
    t = TaskCreate(**data)
    assert t.title == "A task"
    assert t.description == "Optional"
    assert t.status == TaskStatus.TODO
    assert t.priority == TaskPriority.MEDIUM
    assert t.assigned_to is None
    assert t.due_date is None


def test_task_create_title_min_length():
    with pytest.raises(ValidationError):
        TaskCreate(title="")


def test_task_create_title_max_length():
    with pytest.raises(ValidationError):
        TaskCreate(title="x" * 256)


def test_task_create_invalid_status():
    with pytest.raises(ValidationError):
        TaskCreate(title="Ok", status="invalid")


def test_task_update_partial():
    t = TaskUpdate(title="New title")
    assert t.title == "New title"
    assert t.description is None
    assert t.status is None


def test_task_update_title_empty_rejected():
    with pytest.raises(ValidationError):
        TaskUpdate(title="")