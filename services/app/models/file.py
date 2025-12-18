"""文件模型"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """文件信息，包含 MinIO 元数据"""

    id: str = Field(default_factory=lambda: f"file_{uuid.uuid4().hex[:8]}")
    bucket: str
    path: str
    url: str
    content_type: str = "application/octet-stream"
    size: int = 0
    checksum: Optional[str] = None
    project_id: Optional[str] = None
    recording_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
