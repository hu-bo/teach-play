"""
回放SDK数据模型
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PlaybackStatus(Enum):
    """回放状态"""
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


class StepResultStatus(Enum):
    """步骤执行结果状态"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class PlayerConfig:
    """播放器配置"""
    step_delay: int = 500  # 步骤间延迟(ms)
    click_delay: int = 100  # 点击延迟(ms)
    type_delay: int = 50  # 输入字符间延迟(ms)
    retry_count: int = 3  # 失败重试次数
    retry_delay: int = 1000  # 重试间隔(ms)
    search_region_expand: int = 200  # 搜索区域扩展(px)
    match_threshold: float = 0.8  # 图像匹配阈值
    ocr_timeout: int = 5000  # OCR超时(ms)


@dataclass
class Position:
    """坐标位置"""
    x: int
    y: int


@dataclass
class StepResult:
    """步骤执行结果"""
    step_id: str
    status: StepResultStatus = StepResultStatus.SUCCESS
    message: str = ""
    actual_position: Optional[Position] = None
    duration: int = 0  # 执行耗时(ms)
    retry_count: int = 0
    screenshot: Optional[bytes] = None
    error: Optional[str] = None


@dataclass
class LocatorResult:
    """定位结果"""
    found: bool = False
    position: Optional[Position] = None
    confidence: float = 0.0
    method: str = ""  # ocr, template, fixed
    message: str = ""
