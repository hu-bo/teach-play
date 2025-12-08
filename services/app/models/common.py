"""
通用模型
"""

from pydantic import BaseModel
from typing import Optional


class Position(BaseModel):
    """坐标位置"""
    x: int
    y: int


class Region(BaseModel):
    """区域"""
    x: int
    y: int
    width: int
    height: int


class WindowInfo(BaseModel):
    """窗口信息"""
    window_id: str
    title: str
    process_name: str
    rect: Region
    thumbnail: Optional[str] = None  # base64编码的缩略图


class AIConfig(BaseModel):
    """AI配置"""
    prompt: str
    options: list[dict] = []


class WaitCondition(BaseModel):
    """等待条件"""
    type: str  # text_appear, text_disappear, image_match
    value: str
    region: Optional[Region] = None
    threshold: float = 0.8
