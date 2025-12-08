"""
TeachPlay AI Decision Core
AI决策引擎
"""

from .engine import AIDecisionEngine
from .models import AIConfig, Decision, Option, AnalysisResult

__all__ = [
    "AIDecisionEngine",
    "AIConfig",
    "Decision",
    "Option",
    "AnalysisResult",
]

__version__ = "0.1.0"
