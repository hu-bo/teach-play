"""
PaddleOCR适配器实现
"""

from typing import Optional
from dataclasses import dataclass
from PIL import Image
import numpy as np

from .base import OCRAdapter, TextRegion, Position, BoundingBox


@dataclass
class PaddleConfig:
    """PaddleOCR配置"""
    use_gpu: bool = False
    lang: str = "ch"  # ch, en, japan, korean, etc.
    use_angle_cls: bool = True  # 是否使用方向分类器
    det: bool = True  # 是否进行文字检测
    rec: bool = True  # 是否进行文字识别
    cls: bool = False  # 是否进行方向分类
    show_log: bool = False


class PaddleOCRAdapter(OCRAdapter):
    """PaddleOCR适配器"""

    def __init__(self, config: Optional[PaddleConfig] = None):
        self.config = config or PaddleConfig()
        self._ocr = None
        self._initialized = False

    def _init_ocr(self):
        """延迟初始化OCR引擎"""
        if self._initialized:
            return

        try:
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(
                use_gpu=self.config.use_gpu,
                lang=self.config.lang,
                use_angle_cls=self.config.use_angle_cls,
                det=self.config.det,
                rec=self.config.rec,
                cls=self.config.cls,
                show_log=self.config.show_log
            )
            self._initialized = True

        except ImportError:
            raise RuntimeError(
                "PaddleOCR not installed. "
                "Please install with: pip install paddleocr paddlepaddle"
            )

    def recognize(self, image: Image.Image) -> list[TextRegion]:
        """识别图片中的所有文字"""
        self._init_ocr()

        # 转换为numpy数组
        img_array = np.array(image)

        # 执行OCR
        result = self._ocr.ocr(img_array, cls=self.config.cls)

        regions = []

        if result and result[0]:
            for line in result[0]:
                if len(line) >= 2:
                    # line[0] 是边界框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    # line[1] 是 (文字, 置信度)
                    bbox_points = line[0]
                    text_info = line[1]

                    if len(text_info) >= 2:
                        text = text_info[0]
                        confidence = text_info[1]

                        # 计算边界框
                        x_coords = [p[0] for p in bbox_points]
                        y_coords = [p[1] for p in bbox_points]

                        bbox = BoundingBox(
                            x=int(min(x_coords)),
                            y=int(min(y_coords)),
                            width=int(max(x_coords) - min(x_coords)),
                            height=int(max(y_coords) - min(y_coords))
                        )

                        regions.append(TextRegion(
                            text=text,
                            bbox=bbox,
                            confidence=float(confidence)
                        ))

        return regions

    def find_text(self, image: Image.Image, text: str) -> Optional[Position]:
        """查找指定文字的位置"""
        regions = self.recognize(image)

        # 精确匹配
        for region in regions:
            if text == region.text:
                return region.center

        # 包含匹配
        for region in regions:
            if text in region.text:
                return region.center

        return None


class PaddleOCRService:
    """
    PaddleOCR HTTP服务包装
    用于远程调用OCR服务
    """

    def __init__(self, endpoint: str = "http://localhost:8001"):
        self.endpoint = endpoint

    def recognize(self, image: Image.Image) -> list[TextRegion]:
        """通过HTTP调用OCR服务"""
        import requests
        import io
        import base64

        # 将图片转为base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        # 发送请求
        response = requests.post(
            f"{self.endpoint}/ocr",
            json={"image": img_base64}
        )

        if response.status_code != 200:
            raise RuntimeError(f"OCR service error: {response.text}")

        result = response.json()
        regions = []

        for item in result.get("regions", []):
            regions.append(TextRegion(
                text=item["text"],
                bbox=BoundingBox(**item["bbox"]),
                confidence=item["confidence"]
            ))

        return regions

    def find_text(self, image: Image.Image, text: str) -> Optional[Position]:
        """查找指定文字的位置"""
        regions = self.recognize(image)

        for region in regions:
            if text in region.text:
                return region.center

        return None
