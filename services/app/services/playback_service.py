"""
回放控制服务
"""

import time
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

# SDK imports
try:
    from playback import Player, PlayerConfig, PlaybackStatus as SDKPlaybackStatus
except ImportError:
    Player = None
    PlayerConfig = None
    SDKPlaybackStatus = None

from ..models.recording import Recording, Step
from .recording_service import RecordingService


class PlaybackStatus(str, Enum):
    """回放状态"""
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class StepLog:
    """步骤执行日志"""
    step_id: str
    status: str  # success, failed, skipped
    message: str = ""
    duration: int = 0  # ms
    timestamp: int = 0


@dataclass
class PlaybackState:
    """回放状态"""
    status: PlaybackStatus = PlaybackStatus.IDLE
    recording_id: Optional[str] = None
    current_step: int = 0
    total_steps: int = 0
    start_time: Optional[int] = None
    duration: int = 0  # ms
    logs: list[StepLog] = field(default_factory=list)
    error: Optional[str] = None


class PlaybackServiceSingleton:
    """回放服务单例"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._player: Optional[Player] = None
        self._state = PlaybackState()
        self._recording: Optional[Recording] = None
        self._initialized = True

    def start(self, recording_id: str, start_index: int = 0) -> PlaybackState:
        """开始执行"""
        if self._state.status == PlaybackStatus.PLAYING:
            raise RuntimeError("Already playing")

        # 加载录制
        recording = RecordingService.get_recording(recording_id)
        if not recording:
            raise ValueError(f"Recording {recording_id} not found")

        self._recording = recording
        self._state = PlaybackState(
            status=PlaybackStatus.PLAYING,
            recording_id=recording_id,
            current_step=start_index,
            total_steps=len(recording.steps),
            start_time=int(time.time() * 1000),
            logs=[]
        )

        # 启动播放器
        if Player is not None:
            self._player = Player(PlayerConfig())

            # 设置回调
            def on_step(step_dict, result):
                self._state.current_step += 1
                self._state.logs.append(StepLog(
                    step_id=step_dict.get("id", ""),
                    status=result.status.value,
                    message=result.message,
                    duration=result.duration,
                    timestamp=int(time.time() * 1000)
                ))

            def on_status_change(status):
                self._state.status = PlaybackStatus(status.value)
                if status.value == "error":
                    self._state.error = "Playback error"

            self._player.on_step(on_step)
            self._player.on_status_change(on_status_change)

            # 加载并执行
            self._player.load(recording.model_dump())
            self._player.play(start_index)
        else:
            # 模拟执行
            self._simulate_playback(recording, start_index)

        return self._state

    def pause(self) -> PlaybackState:
        """暂停执行"""
        if self._state.status != PlaybackStatus.PLAYING:
            return self._state

        if self._player:
            self._player.pause()

        self._state.status = PlaybackStatus.PAUSED
        return self._state

    def resume(self) -> PlaybackState:
        """继续执行"""
        if self._state.status != PlaybackStatus.PAUSED:
            return self._state

        if self._player:
            self._player.resume()

        self._state.status = PlaybackStatus.PLAYING
        return self._state

    def stop(self) -> PlaybackState:
        """停止执行"""
        if self._player:
            self._player.stop()
            self._player = None

        self._state.status = PlaybackStatus.STOPPED
        self._update_duration()
        return self._state

    def get_status(self) -> PlaybackState:
        """获取执行状态"""
        self._update_duration()
        return self._state

    def get_logs(self) -> list[StepLog]:
        """获取执行日志"""
        return self._state.logs

    def _update_duration(self):
        """更新执行时长"""
        if self._state.start_time:
            self._state.duration = int(time.time() * 1000) - self._state.start_time

    def _simulate_playback(self, recording: Recording, start_index: int):
        """模拟执行（SDK未安装时）"""
        import threading

        def run():
            for i, step in enumerate(recording.steps[start_index:], start_index):
                if self._state.status != PlaybackStatus.PLAYING:
                    break

                # 模拟执行延迟
                time.sleep(0.5)

                self._state.current_step = i + 1
                self._state.logs.append(StepLog(
                    step_id=step.id,
                    status="success",
                    message="Simulated execution",
                    duration=500,
                    timestamp=int(time.time() * 1000)
                ))

            if self._state.status == PlaybackStatus.PLAYING:
                self._state.status = PlaybackStatus.COMPLETED

        thread = threading.Thread(target=run, daemon=True)
        thread.start()


# 全局单例
PlaybackService = PlaybackServiceSingleton()
