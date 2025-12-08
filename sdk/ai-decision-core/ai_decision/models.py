"""
AI决策引擎数据模型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Position:
    """坐标位置"""
    x: int
    y: int


@dataclass
class Region:
    """区域"""
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
class Option:
    """可选项"""
    label: str
    region: Region
    description: str = ""


@dataclass
class Decision:
    """决策结果"""
    selected_option: Optional[str] = None
    position: Optional[Position] = None
    confidence: float = 0.0
    reasoning: str = ""
    raw_response: str = ""


@dataclass
class AnalysisResult:
    """屏幕分析结果"""
    description: str = ""
    elements: list[dict] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    raw_response: str = ""


@dataclass
class AIConfig:
    """AI配置"""
    provider: str = "openai"  # openai, anthropic
    model: str = "gpt-4o"  # gpt-4o, claude-3-5-sonnet
    api_key: str = ""
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.3
    timeout: int = 30  # 超时时间（秒）
