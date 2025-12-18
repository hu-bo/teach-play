"""
屏幕捕获模块
支持 Windows (DXGI) 和 macOS (ScreenCaptureKit/CGWindowListCreateImage)
"""

import platform
import io
from typing import Optional
from PIL import Image

from .models import WindowInfo, Region


class ScreenCapture:
    """屏幕捕获器"""

    def __init__(self):
        self._platform = platform.system()
        self._capturer = self._init_capturer()

    def _init_capturer(self):
        """初始化平台特定的捕获器"""
        if self._platform == "Darwin":
            return MacOSCapture()
        elif self._platform == "Windows":
            return WindowsCapture()
        else:
            raise NotImplementedError(f"Platform {self._platform} not supported")

    def list_windows(self) -> list[WindowInfo]:
        """获取窗口列表"""
        return self._capturer.list_windows()

    def capture_window(self, window_id: str) -> Optional[Image.Image]:
        """捕获指定窗口"""
        return self._capturer.capture_window(window_id)

    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """捕获指定区域"""
        return self._capturer.capture_region(x, y, width, height)

    def capture_around_point(self, x: int, y: int, size: int = 100) -> Optional[Image.Image]:
        """捕获点击点周围区域"""
        half_size = size // 2
        return self.capture_region(
            x - half_size,
            y - half_size,
            size,
            size
        )


class MacOSCapture:
    """macOS 屏幕捕获实现"""

    def __init__(self):
        try:
            import Quartz
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID,
                CGWindowListCreateImage,
                CGRectMake,
                kCGWindowImageDefault,
                kCGWindowListOptionIncludingWindow,
            )
            self.Quartz = Quartz
            self._available = True
        except ImportError:
            self._available = False
            print("Warning: Quartz not available, screen capture will not work")

    def list_windows(self) -> list[WindowInfo]:
        """获取窗口列表"""
        if not self._available:
            return []

        from Quartz import (
            CGWindowListCopyWindowInfo,
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID,
        )

        windows = []
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )

        for window in window_list:
            window_id = window.get("kCGWindowNumber", 0)
            owner = window.get("kCGWindowOwnerName", "") or ""
            bounds = window.get("kCGWindowBounds", {})
            layer = int(window.get("kCGWindowLayer", 0))

            # 仅保留应用层窗口并排除核心系统进程
            if layer != 0 or owner in ["Window Server", "Dock"]:
                continue

            title = window.get("kCGWindowName")
            if not title:
                title = owner or f"Window {window_id}"

            rect = Region(
                x=int(bounds.get("X", 0)),
                y=int(bounds.get("Y", 0)),
                width=int(bounds.get("Width", 0)),
                height=int(bounds.get("Height", 0))
            )

            # 获取缩略图
            thumbnail = self._get_window_thumbnail(window_id)

            windows.append(WindowInfo(
                window_id=str(window_id),
                title=title,
                process_name=owner,
                rect=rect,
                thumbnail=thumbnail
            ))

        return windows

    def _get_window_thumbnail(self, window_id: int, max_size: int = 200) -> Optional[bytes]:

        """获取窗口缩略图"""
        if not self._available:
            return None

        try:
            from Quartz import (
                CGWindowListCreateImage,
                CGRectNull,
                kCGWindowListOptionIncludingWindow,
                kCGWindowImageDefault,
            )

            image = CGWindowListCreateImage(
                CGRectNull,
                kCGWindowListOptionIncludingWindow,
                window_id,
                kCGWindowImageDefault
            )
 
            if image is None:
                return None

            # 转换为PIL Image
            width = self.Quartz.CGImageGetWidth(image)
            height = self.Quartz.CGImageGetHeight(image)

            if width == 0 or height == 0:
                return None

            # 使用 mss 作为备选方案获取截图
            pil_image = self._cgimage_to_pil(image)
            if pil_image is None:
                return None

            # 缩放为缩略图
            pil_image.thumbnail((max_size, max_size))

            # 转换为bytes
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            return buffer.getvalue()

        except Exception as e:
            print(f"Error getting thumbnail: {e}")
            return None

    def _cgimage_to_pil(self, cg_image) -> Optional[Image.Image]:
        """将CGImage转换为PIL Image"""
        try:
            from Quartz import (
                CGImageGetWidth,
                CGImageGetHeight,
                CGImageGetBytesPerRow,
                CGImageGetDataProvider,
                CGDataProviderCopyData,
            )

            width = CGImageGetWidth(cg_image)
            height = CGImageGetHeight(cg_image)
            bytes_per_row = CGImageGetBytesPerRow(cg_image)

            provider = CGImageGetDataProvider(cg_image)
            data = CGDataProviderCopyData(provider)

            if data is None:
                return None

            # 创建PIL Image
            pil_image = Image.frombytes(
                "RGBA",
                (width, height),
                bytes(data),
                "raw",
                "BGRA",
                bytes_per_row,
                1
            )

            return pil_image.convert("RGB")

        except Exception as e:
            print(f"Error converting CGImage to PIL: {e}")
            return None

    def capture_window(self, window_id: str) -> Optional[Image.Image]:
        """捕获指定窗口"""
        if not self._available:
            return None

        try:
            from Quartz import (
                CGWindowListCreateImage,
                CGRectNull,
                kCGWindowListOptionIncludingWindow,
                kCGWindowImageDefault,
            )

            image = CGWindowListCreateImage(
                CGRectNull,
                kCGWindowListOptionIncludingWindow,
                int(window_id),
                kCGWindowImageDefault
            )

            if image is None:
                return None

            return self._cgimage_to_pil(image)

        except Exception as e:
            print(f"Error capturing window: {e}")
            return None

    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """捕获指定区域"""
        try:
            import mss

            with mss.mss() as sct:
                monitor = {"left": x, "top": y, "width": width, "height": height}
                screenshot = sct.grab(monitor)
                return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        except Exception as e:
            print(f"Error capturing region: {e}")
            return None


class WindowsCapture:
    """Windows 屏幕捕获实现 (DXGI)"""

    def __init__(self):
        self._available = False
        try:
            import win32gui
            import win32ui
            import win32con
            import win32api
            self._available = True
        except ImportError:
            print("Warning: pywin32 not available, using mss fallback")

    def list_windows(self) -> list[WindowInfo]:
        """获取窗口列表"""
        if not self._available:
            return self._list_windows_fallback()

        import win32gui
        import win32process
        import psutil

        windows = []

        def enum_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    rect = win32gui.GetWindowRect(hwnd)
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process = psutil.Process(pid)
                        process_name = process.name()
                    except:
                        process_name = ""

                    windows.append(WindowInfo(
                        window_id=str(hwnd),
                        title=title,
                        process_name=process_name,
                        rect=Region(
                            x=rect[0],
                            y=rect[1],
                            width=rect[2] - rect[0],
                            height=rect[3] - rect[1]
                        )
                    ))
            return True

        win32gui.EnumWindows(enum_callback, None)
        return windows

    def _list_windows_fallback(self) -> list[WindowInfo]:
        """使用mss的fallback实现"""
        import mss

        windows = []
        with mss.mss() as sct:
            for i, monitor in enumerate(sct.monitors[1:], 1):
                windows.append(WindowInfo(
                    window_id=f"monitor_{i}",
                    title=f"Monitor {i}",
                    process_name="",
                    rect=Region(
                        x=monitor["left"],
                        y=monitor["top"],
                        width=monitor["width"],
                        height=monitor["height"]
                    )
                ))
        return windows

    def capture_window(self, window_id: str) -> Optional[Image.Image]:
        """捕获指定窗口"""
        if not self._available or window_id.startswith("monitor_"):
            return self._capture_monitor_fallback(window_id)

        try:
            import win32gui
            import win32ui
            import win32con

            hwnd = int(window_id)
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)

            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

            bmpinfo = bitmap.GetInfo()
            bmpstr = bitmap.GetBitmapBits(True)

            image = Image.frombuffer(
                "RGB",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpstr, "raw", "BGRX", 0, 1
            )

            # 清理
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            return image

        except Exception as e:
            print(f"Error capturing window: {e}")
            return None

    def _capture_monitor_fallback(self, window_id: str) -> Optional[Image.Image]:
        """使用mss捕获显示器"""
        try:
            import mss

            monitor_idx = int(window_id.replace("monitor_", ""))
            with mss.mss() as sct:
                monitor = sct.monitors[monitor_idx]
                screenshot = sct.grab(monitor)
                return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        except Exception as e:
            print(f"Error capturing monitor: {e}")
            return None

    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """捕获指定区域"""
        try:
            import mss

            with mss.mss() as sct:
                monitor = {"left": x, "top": y, "width": width, "height": height}
                screenshot = sct.grab(monitor)
                return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        except Exception as e:
            print(f"Error capturing region: {e}")
            return None
