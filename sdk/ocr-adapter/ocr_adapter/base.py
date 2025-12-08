"""
OCR适配器抽象接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from PIL import Image


@dataclass
class Position:
    """坐标位置"""
    x: int
    y: int


@dataclass
class BoundingBox:
    """边界框"""
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> Position:
        """获取中心点"""
        return Position(
            x=self.x + self.width // 2,
            y=self.y + self.height // 2
        )


@dataclass
class TextRegion:
    """文字区域"""
    text: str
    bbox: BoundingBox
    confidence: float

    @property
    def center(self) -> Position:
        """获取中心点"""
        return self.bbox.center


class OCRAdapter(ABC):
    """OCR适配器抽象基类"""

    @abstractmethod
    def recognize(self, image: Image.Image) -> list[TextRegion]:
        """
        识别图片中的所有文字

        Args:
            image: PIL Image对象

        Returns:
            TextRegion列表
        """
        pass

    @abstractmethod
    def find_text(self, image: Image.Image, text: str) -> Optional[Position]:
        """
        查找指定文字的位置

        Args:
            image: PIL Image对象
            text: 要查找的文字

        Returns:
            文字中心点坐标，未找到返回None
        """
        pass

    def find_all_text(self, image: Image.Image, text: str) -> list[Position]:
        """
        查找所有匹配文字的位置

        Args:
            image: PIL Image对象
            text: 要查找的文字

        Returns:
            所有匹配文字的中心点坐标列表
        """
        regions = self.recognize(image)
        positions = []

        for region in regions:
            if text in region.text:
                positions.append(region.center)

        return positions

    def find_text_fuzzy(
        self,
        image: Image.Image,
        text: str,
        threshold: float = 0.8
    ) -> Optional[Position]:
        """
        模糊查找文字位置

        Args:
            image: PIL Image对象
            text: 要查找的文字
            threshold: 相似度阈值

        Returns:
            最匹配文字的中心点坐标
        """
        regions = self.recognize(image)

        best_match = None
        best_score = 0

        for region in regions:
            score = self._similarity(text, region.text)
            if score >= threshold and score > best_score:
                best_score = score
                best_match = region

        return best_match.center if best_match else None

    def _similarity(self, s1: str, s2: str) -> float:
        """
        计算两个字符串的相似度

        使用简单的包含关系和长度比较
        """
        if s1 == s2:
            return 1.0

        if s1 in s2 or s2 in s1:
            return min(len(s1), len(s2)) / max(len(s1), len(s2))

        # 简单的字符匹配
        common = sum(1 for c in s1 if c in s2)
        return common / max(len(s1), len(s2))
