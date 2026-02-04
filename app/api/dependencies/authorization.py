from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.core.database import get_db
from app.enums import ProjectRole, SystemRole
from app.services import project as project_service


async def require_system_admin(user: CurrentUser) -> CurrentUser:
    if user.system_role != SystemRole.SYSTEM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System admin privileges required",
        )
    return user


SystemAdmin = Annotated[CurrentUser, Depends(require_system_admin)]


class ProjectPermission:
    
    def __init__(self, min_role: ProjectRole):
        self.min_role = min_role
        self._role_hierarchy = {
            ProjectRole.OWNER: 4,
            ProjectRole.ADMIN: 3,
            ProjectRole.MEMBER: 2,
            ProjectRole.VIEWER: 1,
        }
    
    async def __call__(
        self,
        project_id: UUID,
        user: CurrentUser,
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> ProjectRole:
        if user.system_role == SystemRole.SYSTEM_ADMIN:
            return ProjectRole.OWNER
        
        membership = await project_service.get_membership(db, project_id, user.id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this project",
            )
        
        user_role_level = self._role_hierarchy.get(membership.role, 0)
        min_role_level = self._role_hierarchy.get(self.min_role, 0)
        
        if user_role_level < min_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {self.min_role.value} role or higher",
            )
        
        return membership.role


RequireProjectViewer = Annotated[ProjectRole, Depends(ProjectPermission(ProjectRole.VIEWER))]
RequireProjectMember = Annotated[ProjectRole, Depends(ProjectPermission(ProjectRole.MEMBER))]
RequireProjectAdmin = Annotated[ProjectRole, Depends(ProjectPermission(ProjectRole.ADMIN))]
RequireProjectOwner = Annotated[ProjectRole, Depends(ProjectPermission(ProjectRole.OWNER))]
