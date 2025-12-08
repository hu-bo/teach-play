"""
录制器核心模块
"""

import time
import json
import io
import uuid
from typing import Optional, Callable
from pathlib import Path

from .models import (
    Recording,
    Step,
    Event,
    EventType,
    Position,
    TargetWindow,
    Region,
    RecorderConfig,
    WindowInfo,
)
from .capture import ScreenCapture
from .listener import EventListener


class Recorder:
    """录制器"""

    def __init__(self, config: Optional[RecorderConfig] = None):
        self.config = config or RecorderConfig()
        self._capture = ScreenCapture()
        self._listener = EventListener()

        self._recording: Optional[Recording] = None
        self._target_window: Optional[WindowInfo] = None
        self._is_recording = False
        self._step_index = 0

        # OCR 适配器（可选）
        self._ocr_adapter = None

        # 事件回调
        self._on_event_callback: Optional[Callable[[Event], None]] = None
        self._on_step_callback: Optional[Callable[[Step], None]] = None

        # 截图存储回调
        self._save_screenshot_callback: Optional[Callable[[bytes, str], str]] = None

    def set_ocr_adapter(self, adapter) -> None:
        """设置OCR适配器"""
        self._ocr_adapter = adapter

    def set_save_screenshot_callback(self, callback: Callable[[bytes, str], str]) -> None:
        """设置截图保存回调，返回截图URL"""
        self._save_screenshot_callback = callback

    def list_windows(self) -> list[WindowInfo]:
        """获取窗口列表"""
        return self._capture.list_windows()

    def start(
        self,
        window_id: str,
        project_id: str = "",
        name: str = "",
    ) -> None:
        """开始录制"""
        if self._is_recording:
            raise RuntimeError("Already recording")

        # 查找目标窗口
        windows = self.list_windows()
        target = None
        for w in windows:
            if w.window_id == window_id:
                target = w
                break

        if not target:
            raise ValueError(f"Window {window_id} not found")

        self._target_window = target
        self._is_recording = True
        self._step_index = 0

        # 创建录制记录
        self._recording = Recording(
            id=f"rec_{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            name=name or f"Recording {time.strftime('%Y-%m-%d %H:%M:%S')}",
            target_window=TargetWindow(
                title=target.title,
                process_name=target.process_name,
                rect=target.rect
            ),
            steps=[]
        )

        # 开始监听事件
        self._listener.start(self._handle_event)

    def stop(self) -> Recording:
        """停止录制"""
        if not self._is_recording:
            raise RuntimeError("Not recording")

        self._is_recording = False
        self._listener.stop()

        recording = self._recording
        self._recording = None
        self._target_window = None

        return recording

    def on_event(self, callback: Callable[[Event], None]) -> None:
        """注册事件回调"""
        self._on_event_callback = callback

    def on_step(self, callback: Callable[[Step], None]) -> None:
        """注册步骤回调"""
        self._on_step_callback = callback

    def _handle_event(self, event: Event) -> None:
        """处理事件"""
        if not self._is_recording:
            return

        # 触发事件回调
        if self._on_event_callback:
            self._on_event_callback(event)

        # 将事件转换为步骤
        step = self._event_to_step(event)
        if step:
            self._recording.steps.append(step)

            # 触发步骤回调
            if self._on_step_callback:
                self._on_step_callback(step)

    def _event_to_step(self, event: Event) -> Optional[Step]:
        """将事件转换为步骤"""
        step = Step(
            index=self._step_index,
            timestamp=event.timestamp,
            position=event.position,
        )

        self._step_index += 1

        # 根据事件类型设置步骤属性
        if event.event_type == EventType.CLICK:
            step.step_type = "click"
            step.mode = "smart"  # 默认智能模式
            step.button = event.data.get("button", "left")
            self._capture_and_ocr(step, event.position)

        elif event.event_type == EventType.DOUBLE_CLICK:
            step.step_type = "click"
            step.mode = "smart"
            step.button = "left"
            step.description = "双击"
            self._capture_and_ocr(step, event.position)

        elif event.event_type == EventType.RIGHT_CLICK:
            step.step_type = "click"
            step.mode = "smart"
            step.button = "right"
            self._capture_and_ocr(step, event.position)

        elif event.event_type == EventType.SCROLL:
            step.step_type = "scroll"
            step.mode = "fixed"
            step.direction = event.data.get("direction", "down")
            step.amount = event.data.get("amount", 100)

        elif event.event_type == EventType.DRAG:
            step.step_type = "drag"
            step.mode = "fixed"
            from_data = event.data.get("from", {})
            to_data = event.data.get("to", {})
            step.from_position = Position(from_data.get("x", 0), from_data.get("y", 0))
            step.to_position = Position(to_data.get("x", 0), to_data.get("y", 0))

        elif event.event_type == EventType.INPUT:
            step.step_type = "input"
            step.mode = "fixed"
            step.input_text = event.data.get("text", "")

        elif event.event_type == EventType.KEY:
            step.step_type = "key"
            step.mode = "fixed"
            step.key = event.data.get("key", "")

        elif event.event_type == EventType.FILE_SELECT:
            step.step_type = "file_select"
            step.mode = "fixed"
            step.file_path = event.data.get("file_path", "")

        else:
            return None

        return step

    def _capture_and_ocr(self, step: Step, position: Position) -> None:
        """捕获截图并进行OCR识别"""
        # 捕获点击区域
        image = self._capture.capture_around_point(
            position.x,
            position.y,
            self.config.capture_region_size
        )

        if image:
            # 保存截图
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            screenshot_bytes = buffer.getvalue()

            if self._save_screenshot_callback:
                step.screenshot = self._save_screenshot_callback(
                    screenshot_bytes,
                    f"{step.id}.png"
                )

            # OCR识别
            if self.config.enable_ocr and self._ocr_adapter:
                try:
                    text_regions = self._ocr_adapter.recognize(image)
                    if text_regions:
                        # 取置信度最高的文字
                        best_region = max(text_regions, key=lambda x: x.confidence)
                        step.text = best_region.text
                except Exception as e:
                    print(f"OCR error: {e}")

    def save_to_file(self, recording: Recording, filepath: str) -> None:
        """保存录制到文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(recording.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_from_file(filepath: str) -> Recording:
        """从文件加载录制"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 转换为Recording对象
        target_window = None
        if data.get("target_window"):
            tw = data["target_window"]
            target_window = TargetWindow(
                title=tw["title"],
                process_name=tw["process_name"],
                rect=Region(**tw["rect"])
            )

        steps = []
        for step_data in data.get("steps", []):
            step = Step(
                id=step_data.get("id", ""),
                index=step_data.get("index", 0),
                step_type=step_data.get("type", "click"),
                mode=step_data.get("mode", "fixed"),
                timestamp=step_data.get("timestamp", 0),
                description=step_data.get("description", ""),
            )

            if "position" in step_data:
                step.position = Position(**step_data["position"])
            if "text" in step_data:
                step.text = step_data["text"]
            if "screenshot" in step_data:
                step.screenshot = step_data["screenshot"]
            if "button" in step_data:
                step.button = step_data["button"]
            if "direction" in step_data:
                step.direction = step_data["direction"]
            if "amount" in step_data:
                step.amount = step_data["amount"]
            if "from" in step_data:
                step.from_position = Position(**step_data["from"])
            if "to" in step_data:
                step.to_position = Position(**step_data["to"])
            if "key" in step_data:
                step.key = step_data["key"]
            if "file_path" in step_data:
                step.file_path = step_data["file_path"]
            if "duration" in step_data:
                step.duration = step_data["duration"]
            if "timeout" in step_data:
                step.timeout = step_data["timeout"]

            steps.append(step)

        return Recording(
            id=data.get("id", ""),
            project_id=data.get("project_id", ""),
            name=data.get("name", ""),
            created_at=data.get("created_at", ""),
            target_window=target_window,
            steps=steps
        )
