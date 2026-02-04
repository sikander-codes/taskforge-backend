from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def get_task(db: AsyncSession, task_id: UUID) -> Task | None:
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def get_project_tasks(db: AsyncSession, project_id: UUID) -> list[Task]:
    result = await db.execute(
        select(Task).where(Task.project_id == project_id, Task.deleted_at.is_(None))
    )
    return list(result.scalars().all())


async def create_task(
    db: AsyncSession, project_id: UUID, task_data: TaskCreate, creator_id: UUID
) -> Task:
    task = Task(
        project_id=project_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        assigned_to=task_data.assigned_to,
        due_date=task_data.due_date,
        created_by=creator_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(db: AsyncSession, task: Task, task_data: TaskUpdate) -> Task:
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    task.deleted_at = datetime.now()
    await db.commit()
