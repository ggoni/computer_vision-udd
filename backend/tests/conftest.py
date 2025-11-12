"""Shared pytest configuration."""

import os

from src.core.config import get_settings


# Ensure test environment uses NullPool and other test-specific defaults
os.environ.setdefault("APP_ENV", "test")
get_settings.cache_clear()