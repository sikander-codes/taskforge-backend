from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.enums import ProjectRole
from app.models.project import Project, ProjectMember
from app.schemas.project import ProjectCreate, ProjectUpdate


async def get_project(db: AsyncSession, project_id: UUID) -> Optional[Project]:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def get_user_projects(db: AsyncSession, user_id: UUID) -> list[Project]:
    result = await db.execute(
        select(Project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == user_id, Project.deleted_at.is_(None))
        .options(selectinload(Project.members))
    )
    return list[Project](result.scalars().all())


async def create_project(
    db: AsyncSession, project_data: ProjectCreate, creator_id: UUID
) -> Project:
    project = Project(
        name=project_data.name,
        description=project_data.description,
        created_by=creator_id,
    )
    db.add(project)
    await db.flush()
    
    member = ProjectMember(
        project_id=project.id,
        user_id=creator_id,
        role=ProjectRole.OWNER,
    )
    db.add(member)
    
    await db.commit()
    await db.refresh(project)
    return project


async def update_project(
    db: AsyncSession, project: Project, project_data: ProjectUpdate
) -> Project:
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project: Project) -> None:
    project.deleted_at = datetime.now()
    await db.commit()


async def get_membership(
    db: AsyncSession, project_id: UUID, user_id: UUID
) -> Optional[ProjectMember]:
    result = await db.execute(
        select(ProjectMember)
        .where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def add_member(
    db: AsyncSession, project_id: UUID, user_id: UUID, role: ProjectRole
) -> ProjectMember:
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def update_member_role(
    db: AsyncSession, member: ProjectMember, role: ProjectRole
) -> ProjectMember:
    member.role = role
    await db.commit()
    await db.refresh(member)
    return member


async def remove_member(db: AsyncSession, member: ProjectMember) -> None:
    await db.delete(member)
    await db.commit()


async def get_project_members(
    db: AsyncSession, project_id: UUID
) -> list[ProjectMember]:
    result = await db.execute(
        select(ProjectMember).where(ProjectMember.project_id == project_id)
    )
    return list(result.scalars().all())
