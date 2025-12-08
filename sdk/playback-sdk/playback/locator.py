"""
元素定位模块
支持 OCR文字定位、图像模板匹配、固定坐标
"""

import io
from typing import Optional
from PIL import Image

from .models import Position, LocatorResult, PlayerConfig


class ElementLocator:
    """元素定位器"""

    def __init__(self, config: Optional[PlayerConfig] = None):
        self.config = config or PlayerConfig()
        self._ocr_adapter = None
        self._screen_capture = None

    def set_ocr_adapter(self, adapter) -> None:
        """设置OCR适配器"""
        self._ocr_adapter = adapter

    def set_screen_capture(self, capture) -> None:
        """设置屏幕捕获器"""
        self._screen_capture = capture

    def locate(
        self,
        text: Optional[str] = None,
        template: Optional[Image.Image] = None,
        fixed_position: Optional[Position] = None,
        hint_position: Optional[Position] = None,
    ) -> LocatorResult:
        """
        定位元素

        优先级:
        1. OCR 文字定位 (如果提供了 text)
        2. 模板匹配 (如果提供了 template)
        3. 固定坐标 (如果提供了 fixed_position)

        Args:
            text: 要查找的文字
            template: 模板图片
            fixed_position: 固定坐标
            hint_position: 提示坐标，用于缩小搜索范围
        """
        # 1. 尝试 OCR 文字定位
        if text and self._ocr_adapter and self._screen_capture:
            result = self._locate_by_text(text, hint_position)
            if result.found:
                return result

        # 2. 尝试模板匹配
        if template and self._screen_capture:
            result = self._locate_by_template(template, hint_position)
            if result.found:
                return result

        # 3. 使用固定坐标
        if fixed_position:
            return LocatorResult(
                found=True,
                position=fixed_position,
                confidence=1.0,
                method="fixed",
                message="Using fixed position"
            )

        return LocatorResult(
            found=False,
            message="No element found"
        )

    def _locate_by_text(
        self,
        text: str,
        hint_position: Optional[Position] = None
    ) -> LocatorResult:
        """通过OCR文字定位"""
        try:
            # 获取搜索区域
            if hint_position:
                # 在提示位置周围搜索
                expand = self.config.search_region_expand
                x = max(0, hint_position.x - expand)
                y = max(0, hint_position.y - expand)
                width = expand * 2
                height = expand * 2
                screenshot = self._screen_capture.capture_region(x, y, width, height)
                offset = Position(x, y)
            else:
                # 全屏搜索
                screenshot = self._screen_capture.capture_window(None)
                offset = Position(0, 0)

            if not screenshot:
                return LocatorResult(found=False, message="Failed to capture screen")

            # OCR 识别
            position = self._ocr_adapter.find_text(screenshot, text)
            if position:
                # 转换为屏幕坐标
                screen_pos = Position(
                    position.x + offset.x,
                    position.y + offset.y
                )
                return LocatorResult(
                    found=True,
                    position=screen_pos,
                    confidence=0.9,
                    method="ocr",
                    message=f"Found text: {text}"
                )

            return LocatorResult(
                found=False,
                method="ocr",
                message=f"Text not found: {text}"
            )

        except Exception as e:
            return LocatorResult(
                found=False,
                method="ocr",
                message=f"OCR error: {str(e)}"
            )

    def _locate_by_template(
        self,
        template: Image.Image,
        hint_position: Optional[Position] = None
    ) -> LocatorResult:
        """通过模板匹配定位"""
        try:
            import cv2
            import numpy as np

            # 获取搜索区域
            if hint_position:
                expand = self.config.search_region_expand
                x = max(0, hint_position.x - expand)
                y = max(0, hint_position.y - expand)
                width = expand * 2
                height = expand * 2
                screenshot = self._screen_capture.capture_region(x, y, width, height)
                offset = Position(x, y)
            else:
                screenshot = self._screen_capture.capture_window(None)
                offset = Position(0, 0)

            if not screenshot:
                return LocatorResult(found=False, message="Failed to capture screen")

            # 转换为 OpenCV 格式
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            template_cv = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)

            # 模板匹配
            result = cv2.matchTemplate(screenshot_cv, template_cv, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= self.config.match_threshold:
                # 计算中心点
                template_h, template_w = template_cv.shape[:2]
                center_x = max_loc[0] + template_w // 2 + offset.x
                center_y = max_loc[1] + template_h // 2 + offset.y

                return LocatorResult(
                    found=True,
                    position=Position(center_x, center_y),
                    confidence=float(max_val),
                    method="template",
                    message=f"Template matched with confidence: {max_val:.2f}"
                )

            return LocatorResult(
                found=False,
                method="template",
                confidence=float(max_val),
                message=f"Template match confidence too low: {max_val:.2f}"
            )

        except ImportError:
            return LocatorResult(
                found=False,
                method="template",
                message="OpenCV not available"
            )
        except Exception as e:
            return LocatorResult(
                found=False,
                method="template",
                message=f"Template matching error: {str(e)}"
            )

    def wait_for_text(
        self,
        text: str,
        timeout: int = 30000,
        interval: int = 500
    ) -> LocatorResult:
        """等待文字出现"""
        import time

        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout:
            result = self._locate_by_text(text, None)
            if result.found:
                return result
            time.sleep(interval / 1000)

        return LocatorResult(
            found=False,
            method="ocr",
            message=f"Timeout waiting for text: {text}"
        )

    def wait_for_template(
        self,
        template: Image.Image,
        timeout: int = 30000,
        interval: int = 500
    ) -> LocatorResult:
        """等待图像出现"""
        import time

        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout:
            result = self._locate_by_template(template, None)
            if result.found:
                return result
            time.sleep(interval / 1000)

        return LocatorResult(
            found=False,
            method="template",
            message="Timeout waiting for template"
        )
