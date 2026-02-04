from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.authorization import RequireProjectMember
from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import project as project_service
from app.services import task as task_service

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["Tasks"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: UUID,
    task_data: TaskCreate,
    user: CurrentUser,
    db: DbSession,
    _role: RequireProjectMember,
):
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if task_data.assigned_to:
        assignee = await project_service.get_membership(db, project_id, task_data.assigned_to)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user is not a project member",
            )

    return await task_service.create_task(db, project_id, task_data, user.id)


@router.get("", response_model=list[TaskResponse])
async def list_project_tasks(
    project_id: UUID,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectMember,
):
    return await task_service.get_project_tasks(db, project_id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    project_id: UUID,
    task_id: UUID,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectMember,
):
    task = await task_service.get_task(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    project_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectMember,
):
    task = await task_service.get_task(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task_data.assigned_to is not None:
        assignee = await project_service.get_membership(db, project_id, task_data.assigned_to)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user is not a project member",
            )

    return await task_service.update_task(db, task, task_data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    project_id: UUID,
    task_id: UUID,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectMember,
):
    task = await task_service.get_task(db, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    await task_service.delete_task(db, task)
