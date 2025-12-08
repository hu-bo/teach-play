"""
事件监听模块
监听键盘、鼠标事件
"""

import time
import threading
from typing import Callable, Optional
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key

from .models import Event, EventType, Position


class EventListener:
    """事件监听器"""

    def __init__(self):
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._callback: Optional[Callable[[Event], None]] = None
        self._running = False

        # 拖拽状态
        self._drag_start: Optional[Position] = None
        self._is_dragging = False

        # 双击检测
        self._last_click_time = 0
        self._last_click_pos: Optional[Position] = None
        self._double_click_threshold = 0.3  # 300ms
        self._double_click_distance = 5  # 5px

        # 输入缓冲
        self._input_buffer = ""
        self._input_timer: Optional[threading.Timer] = None
        self._input_position: Optional[Position] = None
        self._input_flush_delay = 0.5  # 500ms 无输入后提交

        # 当前鼠标位置
        self._current_mouse_pos = Position(0, 0)

    def start(self, callback: Callable[[Event], None]) -> None:
        """开始监听"""
        if self._running:
            return

        self._callback = callback
        self._running = True

        # 启动鼠标监听
        self._mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_scroll=self._on_scroll,
            on_move=self._on_move
        )
        self._mouse_listener.start()

        # 启动键盘监听
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._keyboard_listener.start()

    def stop(self) -> None:
        """停止监听"""
        self._running = False

        # 提交未完成的输入
        self._flush_input()

        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

    def _emit_event(self, event: Event) -> None:
        """触发事件"""
        if self._callback and self._running:
            self._callback(event)

    def _on_move(self, x: int, y: int) -> None:
        """鼠标移动"""
        self._current_mouse_pos = Position(int(x), int(y))

        # 检测拖拽
        if self._drag_start:
            self._is_dragging = True

    def _on_click(self, x: int, y: int, button: Button, pressed: bool) -> None:
        """鼠标点击"""
        pos = Position(int(x), int(y))
        current_time = time.time()

        if pressed:
            # 按下时记录拖拽起点
            self._drag_start = pos
            self._is_dragging = False
        else:
            # 释放时判断是点击还是拖拽
            if self._is_dragging and self._drag_start:
                # 拖拽事件
                self._emit_event(Event(
                    event_type=EventType.DRAG,
                    position=self._drag_start,
                    timestamp=int(current_time * 1000),
                    data={
                        "from": {"x": self._drag_start.x, "y": self._drag_start.y},
                        "to": {"x": pos.x, "y": pos.y}
                    }
                ))
            else:
                # 点击事件
                event_type = EventType.CLICK

                # 检测右键
                if button == Button.right:
                    event_type = EventType.RIGHT_CLICK
                # 检测双击
                elif (
                    self._last_click_pos and
                    current_time - self._last_click_time < self._double_click_threshold and
                    abs(pos.x - self._last_click_pos.x) < self._double_click_distance and
                    abs(pos.y - self._last_click_pos.y) < self._double_click_distance
                ):
                    event_type = EventType.DOUBLE_CLICK
                    self._last_click_time = 0  # 重置，避免连续双击
                    self._last_click_pos = None
                else:
                    self._last_click_time = current_time
                    self._last_click_pos = pos

                self._emit_event(Event(
                    event_type=event_type,
                    position=pos,
                    timestamp=int(current_time * 1000),
                    data={"button": button.name if hasattr(button, 'name') else str(button)}
                ))

            # 重置拖拽状态
            self._drag_start = None
            self._is_dragging = False

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """鼠标滚动"""
        direction = "down" if dy < 0 else "up"
        if dx != 0:
            direction = "right" if dx > 0 else "left"

        self._emit_event(Event(
            event_type=EventType.SCROLL,
            position=Position(int(x), int(y)),
            timestamp=int(time.time() * 1000),
            data={
                "direction": direction,
                "amount": abs(dy) if dy != 0 else abs(dx),
                "dx": dx,
                "dy": dy
            }
        ))

    def _on_key_press(self, key) -> None:
        """按键按下"""
        # 判断是否是可打印字符
        try:
            char = key.char
            if char:
                # 可打印字符，加入输入缓冲
                self._add_to_input_buffer(char)
                return
        except AttributeError:
            pass

        # 特殊按键
        key_name = self._get_key_name(key)
        if key_name:
            # 先提交之前的输入
            self._flush_input()

            self._emit_event(Event(
                event_type=EventType.KEY,
                position=self._current_mouse_pos,
                timestamp=int(time.time() * 1000),
                data={"key": key_name}
            ))

    def _on_key_release(self, key) -> None:
        """按键释放"""
        pass  # 目前不需要处理释放事件

    def _get_key_name(self, key) -> Optional[str]:
        """获取按键名称"""
        special_keys = {
            Key.enter: "enter",
            Key.tab: "tab",
            Key.space: "space",
            Key.backspace: "backspace",
            Key.delete: "delete",
            Key.esc: "escape",
            Key.up: "up",
            Key.down: "down",
            Key.left: "left",
            Key.right: "right",
            Key.home: "home",
            Key.end: "end",
            Key.page_up: "page_up",
            Key.page_down: "page_down",
            Key.f1: "f1",
            Key.f2: "f2",
            Key.f3: "f3",
            Key.f4: "f4",
            Key.f5: "f5",
            Key.f6: "f6",
            Key.f7: "f7",
            Key.f8: "f8",
            Key.f9: "f9",
            Key.f10: "f10",
            Key.f11: "f11",
            Key.f12: "f12",
        }

        return special_keys.get(key)

    def _add_to_input_buffer(self, char: str) -> None:
        """添加字符到输入缓冲"""
        if not self._input_buffer:
            self._input_position = self._current_mouse_pos

        self._input_buffer += char

        # 重置定时器
        if self._input_timer:
            self._input_timer.cancel()

        self._input_timer = threading.Timer(self._input_flush_delay, self._flush_input)
        self._input_timer.start()

    def _flush_input(self) -> None:
        """提交输入缓冲"""
        if self._input_buffer:
            self._emit_event(Event(
                event_type=EventType.INPUT,
                position=self._input_position or self._current_mouse_pos,
                timestamp=int(time.time() * 1000),
                data={"text": self._input_buffer}
            ))
            self._input_buffer = ""
            self._input_position = None

        if self._input_timer:
            self._input_timer.cancel()
            self._input_timer = None
