from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums import ProjectRole


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MemberAddRequest(BaseModel):
    user_id: UUID
    role: ProjectRole = ProjectRole.MEMBER


class MemberUpdateRequest(BaseModel):
    role: ProjectRole


class MemberResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    role: ProjectRole
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)
