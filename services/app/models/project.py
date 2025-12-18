"""
项目模型
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ProjectBase(BaseModel):
    """项目基础模型"""
    name: str
    description: str = ""


class ProjectCreate(ProjectBase):
    """创建项目"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目"""
    name: Optional[str] = None
    description: Optional[str] = None


class Project(ProjectBase):
    """项目"""
    id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    recordings: list[str] = Field(default_factory=list)  # 录制ID列表

    class Config:
        from_attributes = True
