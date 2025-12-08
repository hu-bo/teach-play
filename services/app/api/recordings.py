"""
录制管理API
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from ..models.recording import (
    Recording,
    RecordingCreate,
    RecordingUpdate,
    Step,
    StepCreate,
    StepUpdate,
)
from ..services.recording_service import RecordingService

router = APIRouter()


@router.get("", response_model=list[Recording])
async def list_recordings(project_id: Optional[str] = None):
    """获取录制列表"""
    return RecordingService.list_recordings(project_id)


@router.post("", response_model=Recording)
async def create_recording(recording: RecordingCreate):
    """创建录制"""
    return RecordingService.create_recording(recording)


@router.get("/{recording_id}", response_model=Recording)
async def get_recording(recording_id: str):
    """获取录制详情"""
    recording = RecordingService.get_recording(recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


@router.put("/{recording_id}", response_model=Recording)
async def update_recording(recording_id: str, recording: RecordingUpdate):
    """更新录制"""
    updated = RecordingService.update_recording(recording_id, recording)
    if not updated:
        raise HTTPException(status_code=404, detail="Recording not found")
    return updated


@router.delete("/{recording_id}")
async def delete_recording(recording_id: str):
    """删除录制"""
    success = RecordingService.delete_recording(recording_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recording not found")
    return {"message": "Recording deleted"}


# 步骤管理

@router.get("/{recording_id}/steps", response_model=list[Step])
async def list_steps(recording_id: str):
    """获取步骤列表"""
    return RecordingService.get_steps(recording_id)


@router.post("/{recording_id}/steps", response_model=Step)
async def add_step(recording_id: str, step: StepCreate):
    """添加步骤"""
    created = RecordingService.add_step(recording_id, step)
    if not created:
        raise HTTPException(status_code=404, detail="Recording not found")
    return created


@router.get("/{recording_id}/steps/{step_id}", response_model=Step)
async def get_step(recording_id: str, step_id: str):
    """获取单个步骤"""
    step = RecordingService.get_step(recording_id, step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    return step


@router.put("/{recording_id}/steps/{step_id}", response_model=Step)
async def update_step(recording_id: str, step_id: str, step: StepUpdate):
    """更新步骤"""
    updated = RecordingService.update_step(recording_id, step_id, step)
    if not updated:
        raise HTTPException(status_code=404, detail="Step not found")
    return updated


@router.delete("/{recording_id}/steps/{step_id}")
async def delete_step(recording_id: str, step_id: str):
    """删除步骤"""
    success = RecordingService.delete_step(recording_id, step_id)
    if not success:
        raise HTTPException(status_code=404, detail="Step not found")
    return {"message": "Step deleted"}


@router.put("/{recording_id}/steps/reorder", response_model=list[Step])
async def reorder_steps(recording_id: str, step_ids: list[str]):
    """重新排序步骤"""
    steps = RecordingService.reorder_steps(recording_id, step_ids)
    if steps is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    return steps
