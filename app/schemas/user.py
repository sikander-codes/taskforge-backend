import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.enums import SystemRole


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    password: str | None = Field(default=None, min_length=8)
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str | None) -> str | None:
        if v is None:
            return v
        
        if not (len(v) >= 8 
                and re.search(r"[A-Z]", v)
                and re.search(r"[a-z]", v) 
                and re.search(r"[!@#$%^&*(),.?\":{}|<>]", v)):
            raise ValueError(
                "Password must be at least 8 characters and contain "
                "uppercase, lowercase, and special characters"
            )
        
        return v


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=50)


class UserResponse(UserBase):
    id: UUID
    username: str | None
    system_role: SystemRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    user: UserResponse
