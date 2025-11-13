"""Tests for core configuration module."""

from src.core.config import Settings, get_settings


def test_settings_loads_defaults():
    """Test that settings loads with default values."""
    settings = get_settings()
    assert settings.APP_ENV is not None
    assert settings.MAX_UPLOAD_SIZE > 0
    assert settings.MODEL_NAME == "huggingface/yolos-tiny"
    assert settings.CONFIDENCE_THRESHOLD == 0.5


def test_settings_paths_creation():
    """Test that settings creates necessary paths."""
    settings = get_settings()
    # Paths should be created during initialization
    assert settings.upload_path.exists()
    assert settings.model_cache_path.exists()


def test_settings_is_cached():
    """Test that get_settings returns the same instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_production_mode_detection():
    """Test production mode detection."""
    settings = Settings(APP_ENV="development")
    assert not settings.is_production

    settings_prod = Settings(APP_ENV="production", SECRET_KEY="test-key")
    assert settings_prod.is_production
