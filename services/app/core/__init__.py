"""
核心配置模块
"""

from .config import settings
from .minio_client import minio_client

__all__ = ["settings", "minio_client"]
