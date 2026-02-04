from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.authorization import SystemAdmin
from app.core.database import get_db
from app.models.role import SystemRole
from app.schemas.user import UserResponse, UserUpdate
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["Users"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


class SystemRoleUpdate(BaseModel):
    system_role: SystemRole


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: CurrentUser,
):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_in: UserUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    if user_in.email and user_in.email != current_user.email:
        existing = await user_service.get_user_by_email(db, user_in.email)
        if existing and existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    if user_in.username and user_in.username != current_user.username:
        existing = await user_service.get_user_by_username(db, user_in.username)
        if existing and existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
    
    return await user_service.update_user(db, current_user, user_in)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user_account(
    current_user: CurrentUser,
    db: DbSession,
):
    await user_service.delete_user(db, current_user)


@router.patch("/admin/{user_id}/role", response_model=UserResponse)
async def update_user_system_role(
    user_id: UUID,
    role_data: SystemRoleUpdate,
    _admin: SystemAdmin,
    db: DbSession,
):
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.system_role = role_data.system_role
    await db.commit()
    await db.refresh(user)
    return user
