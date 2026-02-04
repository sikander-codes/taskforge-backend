import enum


class SystemRole(enum.Enum):
    SYSTEM_ADMIN = "system_admin"
    USER = "user"


class ProjectRole(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
