"""
应用配置
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用设置"""

    # 应用配置
    APP_NAME: str = "TeachPlay"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # API配置
    API_PREFIX: str = "/api"

    # CORS配置
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:1420",
        "http://127.0.0.1:1420",
    ]
    CORS_ORIGIN_REGEX: Optional[str] = r"^(https?|tauri)://(localhost|127\.0\.0\.1)(:\d+)?$"

    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "E01n5BAk0veWLQ6kzCCa"
    MINIO_SECRET_KEY: str = "1vQYGXCfIlVErFY1ifR68gD40irDxgnU9gPs4leE"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "tech-play"

    # 数据库配置
    SQLITE_DB_PATH: str = "data/app.db"

    # AI配置
    AI_PROVIDER: str = "openai"
    AI_MODEL: str = "gpt-4o"
    AI_API_KEY: str = ""
    AI_BASE_URL: Optional[str] = None

    # OCR配置
    OCR_PROVIDER: str = "paddle"  # paddle, llm
    OCR_LANG: str = "ch"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
