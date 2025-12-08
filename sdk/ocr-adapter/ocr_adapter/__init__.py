"""
TeachPlay OCR Adapter
OCR统一接口适配层
"""

from .base import OCRAdapter, TextRegion, Position
from .paddle import PaddleOCRAdapter
from .llm import LLMVisionAdapter

__all__ = [
    "OCRAdapter",
    "TextRegion",
    "Position",
    "PaddleOCRAdapter",
    "LLMVisionAdapter",
]

__version__ = "0.1.0"
