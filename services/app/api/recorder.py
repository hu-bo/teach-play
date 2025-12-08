"""
录制控制API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..models.common import WindowInfo
from ..models.recording import Recording
from ..services.recorder_service import RecorderService

router = APIRouter()


class StartRecordingRequest(BaseModel):
    """开始录制请求"""
    project_id: str
    window_id: str
    name: Optional[str] = None


class RecorderStatusResponse(BaseModel):
    """录制状态响应"""
    is_recording: bool
    recording_id: Optional[str] = None
    project_id: Optional[str] = None
    step_count: int = 0
    duration: int = 0


@router.get("/windows", response_model=list[WindowInfo])
async def list_windows():
    """获取窗口列表"""
    return RecorderService.list_windows()


@router.post("/start", response_model=Recording)
async def start_recording(request: StartRecordingRequest):
    """开始录制"""
    try:
        return RecorderService.start_recording(
            project_id=request.project_id,
            window_id=request.window_id,
            name=request.name
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stop", response_model=Optional[Recording])
async def stop_recording():
    """停止录制"""
    recording = RecorderService.stop_recording()
    if not recording:
        raise HTTPException(status_code=400, detail="Not recording")
    return recording


@router.get("/status", response_model=RecorderStatusResponse)
async def get_recorder_status():
    """获取录制状态"""
    status = RecorderService.get_status()
    return RecorderStatusResponse(
        is_recording=status.is_recording,
        recording_id=status.recording_id,
        project_id=status.project_id,
        step_count=status.step_count,
        duration=status.duration
    )
