"""
回放控制API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..services.playback_service import PlaybackService, PlaybackStatus, StepLog

router = APIRouter()


class StartPlaybackRequest(BaseModel):
    """开始执行请求"""
    recording_id: str
    start_index: int = 0


class PlaybackStatusResponse(BaseModel):
    """执行状态响应"""
    status: str
    recording_id: Optional[str] = None
    current_step: int = 0
    total_steps: int = 0
    duration: int = 0
    error: Optional[str] = None


class StepLogResponse(BaseModel):
    """步骤日志响应"""
    step_id: str
    status: str
    message: str
    duration: int
    timestamp: int


@router.post("/start", response_model=PlaybackStatusResponse)
async def start_playback(request: StartPlaybackRequest):
    """开始执行"""
    try:
        state = PlaybackService.start(
            recording_id=request.recording_id,
            start_index=request.start_index
        )
        return PlaybackStatusResponse(
            status=state.status.value,
            recording_id=state.recording_id,
            current_step=state.current_step,
            total_steps=state.total_steps,
            duration=state.duration,
            error=state.error
        )
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pause", response_model=PlaybackStatusResponse)
async def pause_playback():
    """暂停执行"""
    state = PlaybackService.pause()
    return PlaybackStatusResponse(
        status=state.status.value,
        recording_id=state.recording_id,
        current_step=state.current_step,
        total_steps=state.total_steps,
        duration=state.duration,
        error=state.error
    )


@router.post("/resume", response_model=PlaybackStatusResponse)
async def resume_playback():
    """继续执行"""
    state = PlaybackService.resume()
    return PlaybackStatusResponse(
        status=state.status.value,
        recording_id=state.recording_id,
        current_step=state.current_step,
        total_steps=state.total_steps,
        duration=state.duration,
        error=state.error
    )


@router.post("/stop", response_model=PlaybackStatusResponse)
async def stop_playback():
    """停止执行"""
    state = PlaybackService.stop()
    return PlaybackStatusResponse(
        status=state.status.value,
        recording_id=state.recording_id,
        current_step=state.current_step,
        total_steps=state.total_steps,
        duration=state.duration,
        error=state.error
    )


@router.get("/status", response_model=PlaybackStatusResponse)
async def get_playback_status():
    """获取执行状态"""
    state = PlaybackService.get_status()
    return PlaybackStatusResponse(
        status=state.status.value,
        recording_id=state.recording_id,
        current_step=state.current_step,
        total_steps=state.total_steps,
        duration=state.duration,
        error=state.error
    )


@router.get("/logs", response_model=list[StepLogResponse])
async def get_playback_logs():
    """获取执行日志"""
    logs = PlaybackService.get_logs()
    return [
        StepLogResponse(
            step_id=log.step_id,
            status=log.status,
            message=log.message,
            duration=log.duration,
            timestamp=log.timestamp
        )
        for log in logs
    ]
