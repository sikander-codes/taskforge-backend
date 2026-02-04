from app.models.role import ProjectRole, SystemRole


def can_manage_users(system_role: SystemRole) -> bool:
    return system_role == SystemRole.SYSTEM_ADMIN


def can_manage_project(project_role: ProjectRole) -> bool:
    return project_role in {ProjectRole.OWNER, ProjectRole.ADMIN}


def can_manage_members(project_role: ProjectRole) -> bool:
    return project_role in {ProjectRole.OWNER, ProjectRole.ADMIN}


def can_create_tasks(project_role: ProjectRole) -> bool:
    return project_role in {ProjectRole.OWNER, ProjectRole.ADMIN, ProjectRole.MEMBER}


def can_edit_task(project_role: ProjectRole, is_assignee: bool) -> bool:
    return project_role in {ProjectRole.OWNER, ProjectRole.ADMIN, ProjectRole.MEMBER} or is_assignee


def can_delete_task(project_role: ProjectRole) -> bool:
    return project_role in {ProjectRole.OWNER, ProjectRole.ADMIN}


def can_view_project(project_role: ProjectRole) -> bool:
    return project_role in {ProjectRole.OWNER, ProjectRole.ADMIN, ProjectRole.MEMBER, ProjectRole.VIEWER}
