"""
录制模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid

from .common import Position, Region, AIConfig, WaitCondition


class TargetWindow(BaseModel):
    """目标窗口"""
    title: str
    process_name: str
    rect: Region


class StepBase(BaseModel):
    """步骤基础模型"""
    type: Literal["click", "scroll", "drag", "input", "key", "wait", "file_select"]
    mode: Literal["fixed", "smart", "ai_decision"] = "fixed"
    position: Optional[Position] = None
    text: Optional[str] = None
    screenshot: Optional[str] = None
    description: str = ""

    # click
    button: str = "left"

    # scroll
    direction: Optional[str] = None
    amount: int = 0

    # drag
    from_pos: Optional[Position] = Field(None, alias="from")
    to_pos: Optional[Position] = Field(None, alias="to")

    # input
    input_text: Optional[str] = None

    # key
    key: Optional[str] = None

    # file_select
    file_path: Optional[str] = None

    # wait
    duration: int = 0
    condition: Optional[WaitCondition] = None
    timeout: int = 30000

    # ai_decision
    ai_config: Optional[AIConfig] = None


class StepCreate(StepBase):
    """创建步骤"""
    pass


class StepUpdate(BaseModel):
    """更新步骤"""
    type: Optional[str] = None
    mode: Optional[str] = None
    position: Optional[Position] = None
    text: Optional[str] = None
    screenshot: Optional[str] = None
    description: Optional[str] = None
    button: Optional[str] = None
    direction: Optional[str] = None
    amount: Optional[int] = None
    from_pos: Optional[Position] = Field(None, alias="from")
    to_pos: Optional[Position] = Field(None, alias="to")
    input_text: Optional[str] = None
    key: Optional[str] = None
    file_path: Optional[str] = None
    duration: Optional[int] = None
    condition: Optional[WaitCondition] = None
    timeout: Optional[int] = None
    ai_config: Optional[AIConfig] = None


class Step(StepBase):
    """步骤"""
    id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    index: int = 0
    timestamp: int = 0

    class Config:
        from_attributes = True
        populate_by_name = True


class RecordingBase(BaseModel):
    """录制基础模型"""
    name: str
    project_id: str


class RecordingCreate(RecordingBase):
    """创建录制"""
    pass


class RecordingUpdate(BaseModel):
    """更新录制"""
    name: Optional[str] = None


class Recording(RecordingBase):
    """录制"""
    id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    created_at: datetime = Field(default_factory=datetime.now)
    target_window: Optional[TargetWindow] = None
    steps: list[Step] = Field(default_factory=list)

    class Config:
        from_attributes = True
