from fastapi import APIRouter

from .analyze import router as analyze_router
from .health import router as health_router
from .history import router as history_router
from .ws import router as ws_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(analyze_router, tags=["analyze"])
api_router.include_router(history_router, tags=["history"])
api_router.include_router(ws_router, tags=["websocket"])

__all__ = ["api_router"]