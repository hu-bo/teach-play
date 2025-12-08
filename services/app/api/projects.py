"""
项目管理API
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from ..models.project import Project, ProjectCreate, ProjectUpdate
from ..models.recording import Recording
from ..services.project_service import ProjectService
from ..services.recording_service import RecordingService

router = APIRouter()


@router.get("", response_model=list[Project])
async def list_projects():
    """获取项目列表"""
    return ProjectService.list_projects()


@router.post("", response_model=Project)
async def create_project(project: ProjectCreate):
    """创建项目"""
    return ProjectService.create_project(project)


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """获取项目详情"""
    project = ProjectService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project: ProjectUpdate):
    """更新项目"""
    updated = ProjectService.update_project(project_id, project)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    success = ProjectService.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}


@router.get("/{project_id}/recordings", response_model=list[Recording])
async def list_project_recordings(project_id: str):
    """获取项目下的录制列表"""
    project = ProjectService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return RecordingService.list_recordings(project_id)
