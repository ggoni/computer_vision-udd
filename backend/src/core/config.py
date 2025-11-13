"""Core configuration module using Pydantic Settings.

This module provides centralized configuration management for the computer vision backend.
All configuration is loaded from environment variables with sensible defaults.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Environment
    APP_ENV: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=True, description="Debug mode flag")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/cv_db",
        description="Async PostgreSQL database URL",
    )

    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # File Upload Configuration
    UPLOAD_DIR: str = Field(
        default="storage/uploads",
        description="Directory for uploaded files (relative to backend root)",
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum upload file size in bytes",
    )

    # ML Model Configuration
    MODEL_NAME: str = Field(
        default="hustvl/yolos-tiny",
        description="Hugging Face model identifier for object detection",
    )
    MODEL_CACHE_DIR: str = Field(
        default=".cache/models", description="Directory for cached ML models"
    )
    CONFIDENCE_THRESHOLD: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for detections",
    )

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API server host")
    API_PORT: int = Field(default=8000, description="API server port")

    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # Security (for future use)
    SECRET_KEY: str | None = Field(
        default=None, description="Secret key for sessions/JWT (required in production)"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    @property
    def upload_path(self) -> Path:
        """Get absolute path to upload directory."""
        return Path(__file__).parent.parent.parent / self.UPLOAD_DIR

    @property
    def model_cache_path(self) -> Path:
        """Get absolute path to model cache directory."""
        return Path(__file__).parent.parent.parent / self.MODEL_CACHE_DIR

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV.lower() == "production"

    def model_post_init(self, __context) -> None:
        """Post-initialization validation and setup."""
        # Ensure upload directory exists
        self.upload_path.mkdir(parents=True, exist_ok=True)

        # Ensure model cache directory exists
        self.model_cache_path.mkdir(parents=True, exist_ok=True)

        # Validate production requirements
        if self.is_production and not self.SECRET_KEY:
            raise ValueError("SECRET_KEY is required in production environment")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Singleton settings instance
    """
    return Settings()
