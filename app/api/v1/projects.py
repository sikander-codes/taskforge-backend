from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.authorization import (
    RequireProjectAdmin,
    RequireProjectOwner,
    RequireProjectViewer,
)
from app.core.database import get_db
from app.models.role import ProjectRole
from app.schemas.project import (
    MemberAddRequest,
    MemberResponse,
    MemberUpdateRequest,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services import project as project_service
from app.services import user as user_service

router = APIRouter(prefix="/projects", tags=["Projects"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    user: CurrentUser,
    db: DbSession,
):
    return await project_service.create_project(db, project_data, user.id)


@router.get("", response_model=list[ProjectResponse])
async def list_user_projects(
    user: CurrentUser,
    db: DbSession,
):
    return await project_service.get_user_projects(db, user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectViewer,
):
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectAdmin,
):
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return await project_service.update_project(db, project, project_data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectOwner,
):
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    await project_service.delete_project(db, project)


@router.get("/{project_id}/members", response_model=list[MemberResponse])
async def list_project_members(
    project_id: UUID,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectViewer,
):
    return await project_service.get_project_members(db, project_id)


@router.post(
    "/{project_id}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(
    project_id: UUID,
    member_data: MemberAddRequest,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectAdmin,
):
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    target_user = await user_service.get_user_by_id(db, member_data.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    existing = await project_service.get_membership(db, project_id, member_data.user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a project member",
        )
    
    return await project_service.add_member(
        db, project_id, member_data.user_id, member_data.role
    )


@router.patch("/{project_id}/members/{user_id}", response_model=MemberResponse)
async def update_member_role(
    project_id: UUID,
    user_id: UUID,
    role_data: MemberUpdateRequest,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectAdmin,
):
    member = await project_service.get_membership(db, project_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )
    
    if member.role == ProjectRole.OWNER and role_data.role != ProjectRole.OWNER:
        members = await project_service.get_project_members(db, project_id)
        owner_count = sum(1 for m in members if m.role == ProjectRole.OWNER)
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change role of the last project owner",
            )
    
    return await project_service.update_member_role(db, member, role_data.role)


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: UUID,
    user_id: UUID,
    _user: CurrentUser,
    db: DbSession,
    _role: RequireProjectAdmin,
):
    member = await project_service.get_membership(db, project_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )
    
    if member.role == ProjectRole.OWNER:
        members = await project_service.get_project_members(db, project_id)
        owner_count = sum(1 for m in members if m.role == ProjectRole.OWNER)
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last project owner",
            )
    
    await project_service.remove_member(db, member)
