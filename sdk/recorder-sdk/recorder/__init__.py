"""
TeachPlay Recorder SDK
屏幕捕获、事件监听、步骤记录
"""

from .recorder import Recorder
from .capture import ScreenCapture
from .listener import EventListener
from .models import (
    WindowInfo,
    Recording,
    Step,
    Position,
    Event,
    EventType,
    RecorderConfig,
)

__all__ = [
    "Recorder",
    "ScreenCapture",
    "EventListener",
    "WindowInfo",
    "Recording",
    "Step",
    "Position",
    "Event",
    "EventType",
    "RecorderConfig",
]

__version__ = "0.1.0"
