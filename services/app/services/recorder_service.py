"""
录制控制服务
"""

import base64
import time
from typing import Optional
from dataclasses import dataclass

# SDK imports will be available when SDK is installed
try:
    from recorder import Recorder, RecorderConfig, WindowInfo
except ImportError:
    Recorder = None
    RecorderConfig = None
    WindowInfo = None

from ..models.common import WindowInfo as WindowInfoModel, Region
from ..models.recording import Recording, Step
from ..core.minio_client import minio_client
from .recording_service import RecordingService


@dataclass
class RecorderStatus:
    """录制状态"""
    is_recording: bool = False
    recording_id: Optional[str] = None
    project_id: Optional[str] = None
    step_count: int = 0
    duration: int = 0  # ms
    start_time: Optional[int] = None


class RecorderServiceSingleton:
    """录制服务单例"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._recorder: Optional[Recorder] = None
        self._status = RecorderStatus()
        self._current_recording: Optional[Recording] = None
        self._initialized = True

    def list_windows(self) -> list[WindowInfoModel]:
        """获取窗口列表"""
        if Recorder is None:
            # SDK未安装，返回模拟数据
            return [
                WindowInfoModel(
                    window_id="mock_1",
                    title="Mock Window 1",
                    process_name="mock.exe",
                    rect=Region(x=0, y=0, width=1920, height=1080),
                    thumbnail=None
                )
            ]

        recorder = Recorder(RecorderConfig())
        windows = recorder.list_windows()

        return [
            WindowInfoModel(
                window_id=w.window_id,
                title=w.title,
                process_name=w.process_name,
                rect=Region(
                    x=w.rect.x,
                    y=w.rect.y,
                    width=w.rect.width,
                    height=w.rect.height
                ),
                thumbnail=base64.b64encode(w.thumbnail).decode() if w.thumbnail else None
            )
            for w in windows
        ]

    def start_recording(
        self,
        project_id: str,
        window_id: str,
        name: str = ""
    ) -> Recording:
        """开始录制"""
        if self._status.is_recording:
            raise RuntimeError("Already recording")

        # 创建录制记录
        from .recording_service import RecordingService
        from ..models.recording import RecordingCreate

        recording = RecordingService.create_recording(
            RecordingCreate(
                name=name or f"Recording {time.strftime('%Y-%m-%d %H:%M:%S')}",
                project_id=project_id
            )
        )

        self._current_recording = recording
        self._status = RecorderStatus(
            is_recording=True,
            recording_id=recording.id,
            project_id=project_id,
            start_time=int(time.time() * 1000)
        )

        # 启动录制器
        if Recorder is not None:
            self._recorder = Recorder(RecorderConfig())

            # 设置截图保存回调
            def save_screenshot(data: bytes, filename: str) -> str:
                path = f"screenshots/{recording.id}/{filename}"
                return minio_client.upload_file(data, path, "image/png")

            self._recorder.set_save_screenshot_callback(save_screenshot)

            # 设置步骤回调
            def on_step(step):
                self._status.step_count += 1
                # 转换并保存步骤
                step_model = self._convert_step(step)
                self._current_recording.steps.append(step_model)

            self._recorder.on_step(on_step)

            # 开始录制
            self._recorder.start(window_id, project_id, recording.name)

        return recording

    def stop_recording(self) -> Optional[Recording]:
        """停止录制"""
        if not self._status.is_recording:
            return None

        # 停止录制器
        if self._recorder is not None:
            sdk_recording = self._recorder.stop()
            self._recorder = None

        # 更新状态
        recording = self._current_recording
        self._status = RecorderStatus()
        self._current_recording = None

        if recording:
            # 保存录制
            RecordingService.save_recording(recording)

        return recording

    def get_status(self) -> RecorderStatus:
        """获取录制状态"""
        if self._status.is_recording and self._status.start_time:
            self._status.duration = int(time.time() * 1000) - self._status.start_time

        return self._status

    def _convert_step(self, sdk_step) -> Step:
        """转换SDK步骤为服务模型"""
        from ..models.recording import Step
        from ..models.common import Position

        step = Step(
            id=sdk_step.id,
            index=sdk_step.index,
            type=sdk_step.step_type,
            mode=sdk_step.mode,
            timestamp=sdk_step.timestamp,
            description=sdk_step.description,
        )

        if sdk_step.position:
            step.position = Position(x=sdk_step.position.x, y=sdk_step.position.y)
        if sdk_step.text:
            step.text = sdk_step.text
        if sdk_step.screenshot:
            step.screenshot = sdk_step.screenshot
        if sdk_step.button:
            step.button = sdk_step.button
        if sdk_step.direction:
            step.direction = sdk_step.direction
        if sdk_step.amount:
            step.amount = sdk_step.amount

        return step


# 全局单例
RecorderService = RecorderServiceSingleton()
