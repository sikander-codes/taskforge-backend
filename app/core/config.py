from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
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

    # Security / JWT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str 
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property 
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
