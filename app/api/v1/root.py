from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["Root"])


@router.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "docs": settings.DOCS_URL,
        "health": f"{settings.VERSION_PREFIX}/health",
    }
