"""
数据模型定义
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime
import uuid


class EventType(Enum):
    """事件类型"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    SCROLL = "scroll"
    DRAG = "drag"
    INPUT = "input"
    KEY = "key"
    FILE_SELECT = "file_select"


class StepMode(Enum):
    """步骤执行模式"""
    FIXED = "fixed"
    SMART = "smart"
    AI_DECISION = "ai_decision"


class WaitMode(Enum):
    """等待模式"""
    TIME = "time"
    CONDITION = "condition"


@dataclass
class Position:
    """坐标位置"""
    x: int
    y: int


@dataclass
class Region:
    """区域"""
    x: int
    y: int
    width: int
    height: int


@dataclass
class WindowInfo:
    """窗口信息"""
    window_id: str
    title: str
    process_name: str
    rect: Region
    thumbnail: Optional[bytes] = None


@dataclass
class RecorderConfig:
    """录制器配置"""
    capture_region_size: int = 100  # 点击时截图区域大小
    capture_fps: int = 10  # 屏幕捕获帧率
    enable_ocr: bool = True  # 是否启用OCR
    ocr_lang: str = "ch"  # OCR语言


@dataclass
class Event:
    """事件"""
    event_type: EventType
    position: Position
    timestamp: int
    data: dict = field(default_factory=dict)


@dataclass
class AIConfig:
    """AI决策配置"""
    prompt: str
    options: list = field(default_factory=list)


@dataclass
class WaitCondition:
    """等待条件"""
    condition_type: str  # text_appear, text_disappear, image_match
    value: str
    region: Optional[Region] = None
    threshold: float = 0.8


@dataclass
class Step:
    """录制步骤"""
    id: str = field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    index: int = 0
    step_type: str = "click"  # click, scroll, drag, input, key, wait, file_select
    mode: str = "fixed"  # fixed, smart, ai_decision
    position: Optional[Position] = None
    text: Optional[str] = None
    screenshot: Optional[str] = None
    timestamp: int = 0
    description: str = ""

    # 特定类型字段
    button: str = "left"  # 点击按钮类型
    direction: Optional[str] = None  # 滚动方向
    amount: int = 0  # 滚动量
    from_position: Optional[Position] = None  # 拖拽起点
    to_position: Optional[Position] = None  # 拖拽终点
    input_text: Optional[str] = None  # 输入文字
    key: Optional[str] = None  # 按键
    file_path: Optional[str] = None  # 文件路径

    # 等待相关
    duration: int = 0  # 等待时长(ms)
    condition: Optional[WaitCondition] = None
    timeout: int = 30000  # 超时时间(ms)

    # AI决策相关
    ai_config: Optional[AIConfig] = None


@dataclass
class TargetWindow:
    """目标窗口"""
    title: str
    process_name: str
    rect: Region


@dataclass
class Recording:
    """录制记录"""
    id: str = field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    project_id: str = ""
    name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    target_window: Optional[TargetWindow] = None
    steps: list[Step] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "created_at": self.created_at,
            "target_window": {
                "title": self.target_window.title,
                "process_name": self.target_window.process_name,
                "rect": {
                    "x": self.target_window.rect.x,
                    "y": self.target_window.rect.y,
                    "width": self.target_window.rect.width,
                    "height": self.target_window.rect.height,
                }
            } if self.target_window else None,
            "steps": [self._step_to_dict(step) for step in self.steps]
        }

    def _step_to_dict(self, step: Step) -> dict:
        """步骤转换为字典"""
        result = {
            "id": step.id,
            "index": step.index,
            "type": step.step_type,
            "mode": step.mode,
            "timestamp": step.timestamp,
            "description": step.description,
        }

        if step.position:
            result["position"] = {"x": step.position.x, "y": step.position.y}
        if step.text:
            result["text"] = step.text
        if step.screenshot:
            result["screenshot"] = step.screenshot
        if step.button:
            result["button"] = step.button
        if step.direction:
            result["direction"] = step.direction
        if step.amount:
            result["amount"] = step.amount
        if step.from_position:
            result["from"] = {"x": step.from_position.x, "y": step.from_position.y}
        if step.to_position:
            result["to"] = {"x": step.to_position.x, "y": step.to_position.y}
        if step.input_text:
            result["text"] = step.input_text
        if step.key:
            result["key"] = step.key
        if step.file_path:
            result["file_path"] = step.file_path
        if step.duration:
            result["duration"] = step.duration
        if step.condition:
            result["condition"] = {
                "type": step.condition.condition_type,
                "value": step.condition.value,
                "threshold": step.condition.threshold,
            }
            if step.condition.region:
                result["condition"]["region"] = {
                    "x": step.condition.region.x,
                    "y": step.condition.region.y,
                    "width": step.condition.region.width,
                    "height": step.condition.region.height,
                }
        if step.timeout:
            result["timeout"] = step.timeout
        if step.ai_config:
            result["ai_config"] = {
                "prompt": step.ai_config.prompt,
                "options": step.ai_config.options,
            }

        return result
