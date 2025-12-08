"""
TeachPlay Playback SDK
步骤回放、事件模拟
"""

from .player import Player
from .simulator import EventSimulator
from .locator import ElementLocator
from .models import PlayerConfig, StepResult, PlaybackStatus

__all__ = [
    "Player",
    "EventSimulator",
    "ElementLocator",
    "PlayerConfig",
    "StepResult",
    "PlaybackStatus",
]

__version__ = "0.1.0"
