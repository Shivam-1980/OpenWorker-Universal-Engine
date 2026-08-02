"""
OpenWorker Configuration Module
Manages global system settings, hardware bounds, and environment secrets.
"""

from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "OpenWorker"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    WORKSPACES_DIR: Path = BASE_DIR / "workspaces"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # Security & Limits
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_ARCHIVE_EXTENSIONS: List[str] = [".zip"]
    SESSION_TTL_HOURS: int = 24

    # LLM Provider Configuration
    QWEN_API_KEY: str = Field(default="sk-placeholder", env="QWEN_API_KEY")
    QWEN_BASE_URL: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        env="QWEN_BASE_URL",
    )
    DEFAULT_MODEL: str = "qwen-max"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def setup_directories(self) -> None:
        """Ensure all required runtime directories exist."""
        self.WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.setup_directories()
