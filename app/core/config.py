from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TaskForge API"
    APP_DESCRIPTION: str = (
        "TaskForge is a project task management tool."
        "It allows you to create projects, tasks, and workflows."
    )
    APP_VERSION: str = "0.1.0"
    API_VERSION: str = "1"
    VERSION_PREFIX: str = f"/api/v{API_VERSION}"
    DOCS_URL: str | None = f"{VERSION_PREFIX}/docs"
    REDOC_URL: str | None = f"{VERSION_PREFIX}/redoc"
    ENV: str = "development"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]


settings = Settings()
