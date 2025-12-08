"""
事件模拟模块
模拟鼠标、键盘操作
"""

import platform
import time
from typing import Optional

from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController


class EventSimulator:
    """事件模拟器"""

    def __init__(self, click_delay: int = 100, type_delay: int = 50):
        self._mouse = MouseController()
        self._keyboard = KeyboardController()
        self._click_delay = click_delay / 1000  # 转换为秒
        self._type_delay = type_delay / 1000
        self._platform = platform.system()

    def click(self, x: int, y: int, button: str = "left") -> None:
        """模拟点击"""
        self._mouse.position = (x, y)
        time.sleep(self._click_delay)

        btn = self._get_button(button)
        self._mouse.click(btn)

    def double_click(self, x: int, y: int) -> None:
        """模拟双击"""
        self._mouse.position = (x, y)
        time.sleep(self._click_delay)
        self._mouse.click(Button.left, 2)

    def right_click(self, x: int, y: int) -> None:
        """模拟右键点击"""
        self.click(x, y, "right")

    def scroll(self, x: int, y: int, amount: int, direction: str) -> None:
        """模拟滚动"""
        self._mouse.position = (x, y)
        time.sleep(self._click_delay)

        if direction in ("up", "down"):
            dy = amount if direction == "up" else -amount
            self._mouse.scroll(0, dy)
        else:
            dx = amount if direction == "right" else -amount
            self._mouse.scroll(dx, 0)

    def drag(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5) -> None:
        """模拟拖拽"""
        self._mouse.position = (from_x, from_y)
        time.sleep(self._click_delay)

        self._mouse.press(Button.left)

        # 平滑移动
        steps = max(10, int(duration * 60))
        dx = (to_x - from_x) / steps
        dy = (to_y - from_y) / steps

        for i in range(steps):
            x = int(from_x + dx * (i + 1))
            y = int(from_y + dy * (i + 1))
            self._mouse.position = (x, y)
            time.sleep(duration / steps)

        self._mouse.release(Button.left)

    def type_text(self, text: str, position: Optional[tuple] = None) -> None:
        """模拟输入文字"""
        if position:
            self.click(position[0], position[1])
            time.sleep(self._click_delay)

        for char in text:
            self._keyboard.type(char)
            time.sleep(self._type_delay)

    def press_key(self, key: str) -> None:
        """模拟按键"""
        key_obj = self._get_key(key)
        if key_obj:
            self._keyboard.press(key_obj)
            self._keyboard.release(key_obj)

    def hotkey(self, *keys: str) -> None:
        """模拟组合键"""
        key_objs = [self._get_key(k) for k in keys if self._get_key(k)]

        # 按下所有键
        for key in key_objs:
            self._keyboard.press(key)

        # 释放所有键（逆序）
        for key in reversed(key_objs):
            self._keyboard.release(key)

    def move_to(self, x: int, y: int) -> None:
        """移动鼠标到指定位置"""
        self._mouse.position = (x, y)

    def _get_button(self, button: str) -> Button:
        """获取鼠标按钮"""
        buttons = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle,
        }
        return buttons.get(button.lower(), Button.left)

    def _get_key(self, key: str):
        """获取按键对象"""
        # 特殊键映射
        special_keys = {
            "enter": Key.enter,
            "return": Key.enter,
            "tab": Key.tab,
            "space": Key.space,
            "backspace": Key.backspace,
            "delete": Key.delete,
            "escape": Key.esc,
            "esc": Key.esc,
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "home": Key.home,
            "end": Key.end,
            "page_up": Key.page_up,
            "pageup": Key.page_up,
            "page_down": Key.page_down,
            "pagedown": Key.page_down,
            "ctrl": Key.ctrl,
            "control": Key.ctrl,
            "alt": Key.alt,
            "shift": Key.shift,
            "cmd": Key.cmd,
            "command": Key.cmd,
            "win": Key.cmd if self._platform == "Darwin" else Key.cmd,
            "f1": Key.f1,
            "f2": Key.f2,
            "f3": Key.f3,
            "f4": Key.f4,
            "f5": Key.f5,
            "f6": Key.f6,
            "f7": Key.f7,
            "f8": Key.f8,
            "f9": Key.f9,
            "f10": Key.f10,
            "f11": Key.f11,
            "f12": Key.f12,
        }

        key_lower = key.lower()

        # 检查是否是特殊键
        if key_lower in special_keys:
            return special_keys[key_lower]

        # 处理组合键格式 (如 "ctrl+c")
        if "+" in key:
            return None  # 组合键应该用 hotkey 方法

        # 单个字符
        if len(key) == 1:
            return key

        return None
