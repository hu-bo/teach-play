"""
播放器核心模块
"""

import time
import asyncio
import threading
from typing import Optional, Callable
from PIL import Image
import io

from .models import (
    PlayerConfig,
    PlaybackStatus,
    StepResult,
    StepResultStatus,
    Position,
)
from .simulator import EventSimulator
from .locator import ElementLocator


class Player:
    """回放播放器"""

    def __init__(self, config: Optional[PlayerConfig] = None):
        self.config = config or PlayerConfig()
        self._simulator = EventSimulator(
            click_delay=self.config.click_delay,
            type_delay=self.config.type_delay
        )
        self._locator = ElementLocator(config)

        self._status = PlaybackStatus.IDLE
        self._current_step_index = 0
        self._recording = None
        self._steps = []

        # 回调
        self._on_step_callback: Optional[Callable] = None
        self._on_status_change_callback: Optional[Callable] = None

        # AI 决策引擎
        self._ai_engine = None

        # 屏幕捕获器
        self._screen_capture = None

        # 控制标志
        self._stop_flag = threading.Event()
        self._pause_flag = threading.Event()

        # 日志
        self._logs: list[StepResult] = []

    def set_ocr_adapter(self, adapter) -> None:
        """设置OCR适配器"""
        self._locator.set_ocr_adapter(adapter)

    def set_screen_capture(self, capture) -> None:
        """设置屏幕捕获器"""
        self._screen_capture = capture
        self._locator.set_screen_capture(capture)

    def set_ai_engine(self, engine) -> None:
        """设置AI决策引擎"""
        self._ai_engine = engine

    def load(self, recording: dict) -> None:
        """加载录制数据"""
        self._recording = recording
        self._steps = recording.get("steps", [])
        self._current_step_index = 0
        self._logs = []
        self._set_status(PlaybackStatus.IDLE)

    def on_step(self, callback: Callable[[dict, StepResult], None]) -> None:
        """注册步骤完成回调"""
        self._on_step_callback = callback

    def on_status_change(self, callback: Callable[[PlaybackStatus], None]) -> None:
        """注册状态变更回调"""
        self._on_status_change_callback = callback

    def play(self, start_index: int = 0) -> None:
        """开始执行"""
        if self._status == PlaybackStatus.PLAYING:
            return

        self._current_step_index = start_index
        self._stop_flag.clear()
        self._pause_flag.clear()
        self._set_status(PlaybackStatus.PLAYING)

        # 在新线程中执行
        thread = threading.Thread(target=self._play_loop, daemon=True)
        thread.start()

    def pause(self) -> None:
        """暂停执行"""
        if self._status == PlaybackStatus.PLAYING:
            self._pause_flag.set()
            self._set_status(PlaybackStatus.PAUSED)

    def resume(self) -> None:
        """继续执行"""
        if self._status == PlaybackStatus.PAUSED:
            self._pause_flag.clear()
            self._set_status(PlaybackStatus.PLAYING)

    def stop(self) -> None:
        """停止执行"""
        self._stop_flag.set()
        self._pause_flag.clear()
        self._set_status(PlaybackStatus.STOPPED)

    def get_status(self) -> PlaybackStatus:
        """获取当前状态"""
        return self._status

    def get_current_step(self) -> int:
        """获取当前步骤索引"""
        return self._current_step_index

    def get_logs(self) -> list[StepResult]:
        """获取执行日志"""
        return self._logs

    def _set_status(self, status: PlaybackStatus) -> None:
        """设置状态"""
        self._status = status
        if self._on_status_change_callback:
            self._on_status_change_callback(status)

    def _play_loop(self) -> None:
        """执行循环"""
        while self._current_step_index < len(self._steps):
            # 检查停止标志
            if self._stop_flag.is_set():
                break

            # 检查暂停标志
            while self._pause_flag.is_set():
                time.sleep(0.1)
                if self._stop_flag.is_set():
                    return

            step = self._steps[self._current_step_index]
            result = self._execute_step(step)
            self._logs.append(result)

            # 触发回调
            if self._on_step_callback:
                self._on_step_callback(step, result)

            # 如果失败且未重试成功，停止执行
            if result.status == StepResultStatus.FAILED:
                self._set_status(PlaybackStatus.ERROR)
                return

            self._current_step_index += 1

            # 步骤间延迟
            time.sleep(self.config.step_delay / 1000)

        # 执行完成
        if not self._stop_flag.is_set():
            self._set_status(PlaybackStatus.COMPLETED)

    def _execute_step(self, step: dict) -> StepResult:
        """执行单个步骤"""
        step_id = step.get("id", "")
        step_type = step.get("type", "")
        mode = step.get("mode", "fixed")
        start_time = time.time()

        retry_count = 0
        last_error = None

        while retry_count <= self.config.retry_count:
            try:
                if step_type == "click":
                    return self._execute_click(step, start_time, retry_count)
                elif step_type == "scroll":
                    return self._execute_scroll(step, start_time)
                elif step_type == "drag":
                    return self._execute_drag(step, start_time)
                elif step_type == "input":
                    return self._execute_input(step, start_time)
                elif step_type == "key":
                    return self._execute_key(step, start_time)
                elif step_type == "wait":
                    return self._execute_wait(step, start_time)
                elif step_type == "file_select":
                    return self._execute_file_select(step, start_time)
                else:
                    return StepResult(
                        step_id=step_id,
                        status=StepResultStatus.SKIPPED,
                        message=f"Unknown step type: {step_type}",
                        duration=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                last_error = str(e)
                retry_count += 1
                if retry_count <= self.config.retry_count:
                    time.sleep(self.config.retry_delay / 1000)

        return StepResult(
            step_id=step_id,
            status=StepResultStatus.FAILED,
            message=f"Failed after {retry_count} retries",
            error=last_error,
            duration=int((time.time() - start_time) * 1000),
            retry_count=retry_count
        )

    def _execute_click(self, step: dict, start_time: float, retry_count: int) -> StepResult:
        """执行点击步骤"""
        step_id = step.get("id", "")
        mode = step.get("mode", "fixed")
        button = step.get("button", "left")
        position = step.get("position", {})
        text = step.get("text")
        screenshot_url = step.get("screenshot")

        # 确定点击位置
        if mode == "ai_decision":
            # AI 决策
            actual_pos = self._ai_decide(step)
        elif mode == "smart":
            # 智能定位
            hint_pos = Position(position.get("x", 0), position.get("y", 0)) if position else None
            template = self._load_template(screenshot_url) if screenshot_url else None

            result = self._locator.locate(
                text=text,
                template=template,
                fixed_position=hint_pos,
                hint_position=hint_pos
            )

            if not result.found:
                return StepResult(
                    step_id=step_id,
                    status=StepResultStatus.FAILED,
                    message=result.message,
                    duration=int((time.time() - start_time) * 1000),
                    retry_count=retry_count
                )

            actual_pos = result.position
        else:
            # 固定坐标
            actual_pos = Position(position.get("x", 0), position.get("y", 0))

        # 执行点击
        self._simulator.click(actual_pos.x, actual_pos.y, button)

        return StepResult(
            step_id=step_id,
            status=StepResultStatus.SUCCESS,
            actual_position=actual_pos,
            duration=int((time.time() - start_time) * 1000),
            retry_count=retry_count
        )

    def _execute_scroll(self, step: dict, start_time: float) -> StepResult:
        """执行滚动步骤"""
        position = step.get("position", {})
        direction = step.get("direction", "down")
        amount = step.get("amount", 100)

        x = position.get("x", 0)
        y = position.get("y", 0)

        self._simulator.scroll(x, y, amount, direction)

        return StepResult(
            step_id=step.get("id", ""),
            status=StepResultStatus.SUCCESS,
            actual_position=Position(x, y),
            duration=int((time.time() - start_time) * 1000)
        )

    def _execute_drag(self, step: dict, start_time: float) -> StepResult:
        """执行拖拽步骤"""
        from_pos = step.get("from", {})
        to_pos = step.get("to", {})

        self._simulator.drag(
            from_pos.get("x", 0),
            from_pos.get("y", 0),
            to_pos.get("x", 0),
            to_pos.get("y", 0)
        )

        return StepResult(
            step_id=step.get("id", ""),
            status=StepResultStatus.SUCCESS,
            duration=int((time.time() - start_time) * 1000)
        )

    def _execute_input(self, step: dict, start_time: float) -> StepResult:
        """执行输入步骤"""
        text = step.get("text", "")
        position = step.get("position")

        pos = None
        if position:
            pos = (position.get("x", 0), position.get("y", 0))

        self._simulator.type_text(text, pos)

        return StepResult(
            step_id=step.get("id", ""),
            status=StepResultStatus.SUCCESS,
            duration=int((time.time() - start_time) * 1000)
        )

    def _execute_key(self, step: dict, start_time: float) -> StepResult:
        """执行按键步骤"""
        key = step.get("key", "")

        if "+" in key:
            # 组合键
            keys = key.split("+")
            self._simulator.hotkey(*keys)
        else:
            self._simulator.press_key(key)

        return StepResult(
            step_id=step.get("id", ""),
            status=StepResultStatus.SUCCESS,
            duration=int((time.time() - start_time) * 1000)
        )

    def _execute_wait(self, step: dict, start_time: float) -> StepResult:
        """执行等待步骤"""
        mode = step.get("mode", "time")
        duration = step.get("duration", 0)
        timeout = step.get("timeout", 30000)
        condition = step.get("condition", {})

        if mode == "time":
            time.sleep(duration / 1000)
            return StepResult(
                step_id=step.get("id", ""),
                status=StepResultStatus.SUCCESS,
                message=f"Waited {duration}ms",
                duration=int((time.time() - start_time) * 1000)
            )

        elif mode == "condition":
            condition_type = condition.get("type", "")
            value = condition.get("value", "")

            if condition_type == "text_appear":
                result = self._locator.wait_for_text(value, timeout)
            elif condition_type == "text_disappear":
                # TODO: 实现等待文字消失
                result = self._locator.wait_for_text(value, timeout)
                result.found = not result.found
            elif condition_type == "image_match":
                template = self._load_template(value)
                if template:
                    result = self._locator.wait_for_template(template, timeout)
                else:
                    return StepResult(
                        step_id=step.get("id", ""),
                        status=StepResultStatus.FAILED,
                        message="Template image not found",
                        duration=int((time.time() - start_time) * 1000)
                    )
            else:
                return StepResult(
                    step_id=step.get("id", ""),
                    status=StepResultStatus.FAILED,
                    message=f"Unknown condition type: {condition_type}",
                    duration=int((time.time() - start_time) * 1000)
                )

            if result.found:
                return StepResult(
                    step_id=step.get("id", ""),
                    status=StepResultStatus.SUCCESS,
                    message=result.message,
                    duration=int((time.time() - start_time) * 1000)
                )
            else:
                return StepResult(
                    step_id=step.get("id", ""),
                    status=StepResultStatus.TIMEOUT,
                    message=result.message,
                    duration=int((time.time() - start_time) * 1000)
                )

        return StepResult(
            step_id=step.get("id", ""),
            status=StepResultStatus.SKIPPED,
            message=f"Unknown wait mode: {mode}",
            duration=int((time.time() - start_time) * 1000)
        )

    def _execute_file_select(self, step: dict, start_time: float) -> StepResult:
        """执行文件选择步骤"""
        file_path = step.get("file_path", "")

        # 文件选择通常需要在文件对话框中输入路径
        # 这里简化处理，直接输入路径
        self._simulator.type_text(file_path)
        self._simulator.press_key("enter")

        return StepResult(
            step_id=step.get("id", ""),
            status=StepResultStatus.SUCCESS,
            message=f"Selected file: {file_path}",
            duration=int((time.time() - start_time) * 1000)
        )

    def _ai_decide(self, step: dict) -> Optional[Position]:
        """AI 决策"""
        if not self._ai_engine or not self._screen_capture:
            # 回退到固定坐标
            position = step.get("position", {})
            return Position(position.get("x", 0), position.get("y", 0))

        ai_config = step.get("ai_config", {})
        prompt = ai_config.get("prompt", "")
        options = ai_config.get("options", [])

        # 截取当前屏幕
        screenshot = self._screen_capture.capture_window(None)
        if not screenshot:
            position = step.get("position", {})
            return Position(position.get("x", 0), position.get("y", 0))

        # 调用 AI 引擎决策
        try:
            # 异步转同步调用
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            decision = loop.run_until_complete(
                self._ai_engine.decide(screenshot, prompt, options)
            )
            loop.close()

            if decision and decision.position:
                return decision.position

        except Exception as e:
            print(f"AI decision error: {e}")

        # 回退到固定坐标
        position = step.get("position", {})
        return Position(position.get("x", 0), position.get("y", 0))

    def _load_template(self, url_or_path: str) -> Optional[Image.Image]:
        """加载模板图片"""
        try:
            if url_or_path.startswith("minio://"):
                # TODO: 从 MinIO 加载
                return None
            elif url_or_path.startswith("http"):
                # TODO: 从 HTTP 加载
                return None
            else:
                # 本地文件
                return Image.open(url_or_path)
        except Exception as e:
            print(f"Error loading template: {e}")
            return None
