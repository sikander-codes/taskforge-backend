from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import SystemAdmin
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.schemas.user import LoginRequest, LoginResponse, UserCreate, UserResponse
from app.services import user as user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_in: UserCreate,
    db: DbSession,
):
    existing_user = await user_service.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    if user_in.username:
        existing_user = await user_service.get_user_by_username(db, user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
    
    return await user_service.create_user(db, user_in)


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: DbSession,
):
    user = await user_service.get_user_by_email(db, credentials.email)
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Contact admin for verification.",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    
    access_token = create_access_token(user.id)
    
    return LoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/admin/verify-user", status_code=status.HTTP_200_OK)
async def admin_verify_user(
    email: str,
    db: DbSession,
    _admin: SystemAdmin,
):
    user = await user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user.is_verified:
        return {"message": "User already verified"}
    
    user.is_verified = True
    await db.commit()
    
    return {"message": f"User {email} verified successfully"}
