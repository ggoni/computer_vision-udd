"""Unit tests for OpenRouterOCRService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from src.services.openrouter_ocr_service import OpenRouterOCRService


@pytest.fixture
def mock_image():
    """Create a simple test image."""
    img = Image.new("RGB", (100, 100), color="red")
    return img


@pytest.fixture
def ocr_service():
    """Create OCRService instance with test API key."""
    return OpenRouterOCRService(api_key="sk-test-key")


@pytest.mark.asyncio
async def test_extract_text_success(ocr_service, mock_image):
    """Test successful text extraction."""
    expected_text = "Hello World\nThis is handwritten text"

    with patch("src.services.openrouter_ocr_service.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": expected_text}}]
        }

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        result = await ocr_service.extract_text(mock_image)

        assert result["text"] == expected_text
        assert result["confidence"] == 0.85
        assert result["model"] == "claude-3.5-sonnet"
        assert result["error"] is None


@pytest.mark.asyncio
async def test_extract_text_no_handwriting(ocr_service, mock_image):
    """Test when no handwriting is detected."""
    with patch("src.services.openrouter_ocr_service.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "NO_HANDWRITING"}}]
        }

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        result = await ocr_service.extract_text(mock_image)

        assert result["text"] is None
        assert result["confidence"] == 1.0
        assert result["model"] == "claude-3.5-sonnet"
        assert result["error"] is None


@pytest.mark.asyncio
async def test_extract_text_api_error(ocr_service, mock_image):
    """Test handling of API errors."""
    with patch("src.services.openrouter_ocr_service.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=Exception("API connection failed")
        )

        result = await ocr_service.extract_text(mock_image)

        assert result["text"] is None
        assert result["confidence"] == 0.0
        assert result["error"] is not None
        assert "API connection failed" in result["error"]


@pytest.mark.asyncio
async def test_extract_text_http_error(ocr_service, mock_image):
    """Test handling of HTTP errors."""
    import httpx

    with patch("src.services.openrouter_ocr_service.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "401 Unauthorized", request=None, response=None
            )
        )

        result = await ocr_service.extract_text(mock_image)

        assert result["text"] is None
        assert result["confidence"] == 0.0
        assert result["error"] is not None


@pytest.mark.asyncio
async def test_extract_text_image_conversion(ocr_service):
    """Test automatic RGB conversion for non-RGB images."""
    # Create a grayscale image
    gray_img = Image.new("L", (100, 100), color=128)

    with patch("src.services.openrouter_ocr_service.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test text"}}]
        }

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        result = await ocr_service.extract_text(gray_img)

        # Verify conversion happened and extraction succeeded
        assert result["text"] == "Test text"
        assert result["error"] is None


def test_init_with_custom_api_key():
    """Test service initialization with custom API key."""
    custom_key = "sk-custom-key-12345"
    service = OpenRouterOCRService(api_key=custom_key)

    assert service._api_key == custom_key
    assert service._model == "claude-3.5-sonnet"


def test_init_with_env_api_key():
    """Test service initialization using environment variable."""
    with patch("src.services.openrouter_ocr_service.get_settings") as mock_settings:
        mock_settings.return_value.OPENROUTER_API_KEY = "sk-env-key"
        service = OpenRouterOCRService()

        assert service._api_key == "sk-env-key"
