from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, health, projects, root, tasks, users
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(root.router)
    app.include_router(health.router, prefix=settings.VERSION_PREFIX)
    app.include_router(auth.router, prefix=settings.VERSION_PREFIX)
    app.include_router(users.router, prefix=settings.VERSION_PREFIX)
    app.include_router(projects.router, prefix=settings.VERSION_PREFIX)
    app.include_router(tasks.router, prefix=settings.VERSION_PREFIX)

    return app


app = create_app()
