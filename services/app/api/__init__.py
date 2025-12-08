"""
API路由
"""

from fastapi import APIRouter

from .projects import router as projects_router
from .recordings import router as recordings_router
from .recorder import router as recorder_router
from .playback import router as playback_router
from .files import router as files_router

api_router = APIRouter()

api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(recordings_router, prefix="/recordings", tags=["recordings"])
api_router.include_router(recorder_router, prefix="/record", tags=["recorder"])
api_router.include_router(playback_router, prefix="/playback", tags=["playback"])
api_router.include_router(files_router, tags=["files"])
