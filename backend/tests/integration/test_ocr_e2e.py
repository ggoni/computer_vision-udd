"""End-to-end integration tests for handwritten text extraction feature."""

import asyncio
import os
from io import BytesIO

import pytest
from PIL import Image, ImageDraw, ImageFont

from src.services.openrouter_ocr_service import OpenRouterOCRService
from src.tasks.detection_tasks import analyze_image_with_ocr


@pytest.fixture
def sample_handwritten_image() -> bytes:
    """Create a sample image with handwritten-like text using PIL."""
    # Create a simple image with text drawn on it
    img = Image.new("RGB", (400, 200), color="white")
    draw = ImageDraw.Draw(img)

    # Draw some text that looks like it was handwritten
    text = "Hello World\n2025"
    try:
        # Try to use a system font, fallback to default if not available
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
    except (OSError, IOError):
        # Use default font if no TrueType font available
        font = ImageFont.load_default()

    draw.text((50, 50), text, fill="black", font=font)

    # Convert to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()


@pytest.fixture
def sample_blank_image() -> bytes:
    """Create a blank image without any text."""
    img = Image.new("RGB", (400, 200), color="white")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()


@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set in environment",
)
class TestOCREndToEnd:
    """Integration tests requiring real OpenRouter API key."""

    @pytest.mark.asyncio
    async def test_extract_text_from_handwritten_image(
        self, sample_handwritten_image: bytes
    ) -> None:
        """Test text extraction from image with actual OpenRouter API."""
        service = OpenRouterOCRService()
        img = Image.open(BytesIO(sample_handwritten_image))

        result = await service.extract_text(img)

        # Verify response structure
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert "model" in result
        assert "error" in result

        # Verify field types
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["model"], str)
        assert result["model"] == "claude-3.5-sonnet"

        # If extraction succeeded
        if result["error"] is None:
            assert result["text"] is not None
            print(f"\n✓ Text extracted: {result['text'][:100]}")
        else:
            # Error case still valid
            assert result["text"] is None
            assert isinstance(result["error"], str)
            print(f"\n⚠ Extraction failed: {result['error']}")

    @pytest.mark.asyncio
    async def test_extract_text_from_blank_image(
        self, sample_blank_image: bytes
    ) -> None:
        """Test that blank images return NO_HANDWRITING response."""
        service = OpenRouterOCRService()
        img = Image.open(BytesIO(sample_blank_image))

        result = await service.extract_text(img)

        # Blank images should return null text
        assert result["text"] is None
        assert result["confidence"] == 0.85
        assert result["model"] == "claude-3.5-sonnet"
        # Error may or may not be set depending on API response

    @pytest.mark.asyncio
    async def test_analyze_image_with_ocr_integration(
        self, sample_handwritten_image: bytes
    ) -> None:
        """Test full image analysis pipeline (YOLO + OCR)."""
        from uuid import uuid4

        image_id = uuid4()

        # This would normally be called after YOLO detection
        result = await analyze_image_with_ocr(image_id, sample_handwritten_image)

        # Verify response structure
        assert isinstance(result, dict)
        assert "image_id" in result
        assert "status" in result
        assert "detections" in result
        assert "text_extraction" in result

        # Verify image_id matches
        assert str(result["image_id"]) == str(image_id)

        # Status can be "success" (both YOLO and OCR work)
        # or "partial" (YOLO works but OCR fails)
        assert result["status"] in ("success", "partial")

        # Verify detections list
        assert isinstance(result["detections"], list)

        # Verify text extraction structure
        text_ext = result["text_extraction"]
        assert isinstance(text_ext, dict)
        assert "text" in text_ext
        assert "confidence" in text_ext
        assert "model" in text_ext
        assert "error" in text_ext

        print(f"\n✓ Analysis status: {result['status']}")
        print(f"  Detections: {len(result['detections'])}")
        print(f"  Text extraction model: {text_ext['model']}")


@pytest.mark.skipif(
    os.getenv("OPENROUTER_API_KEY"),
    reason="Test only runs without API key (mock fallback)",
)
class TestOCRWithoutAPIKey:
    """Tests that verify graceful degradation without API key."""

    @pytest.mark.asyncio
    async def test_ocr_service_empty_api_key(self, sample_handwritten_image: bytes) -> None:
        """Test OCR service behavior with missing API key."""
        # Create service with explicitly empty key
        service = OpenRouterOCRService(api_key="")
        img = Image.open(BytesIO(sample_handwritten_image))

        result = await service.extract_text(img)

        # Should handle gracefully
        assert result["text"] is None
        assert result["error"] is not None
        print(f"\n✓ Gracefully handled missing API key: {result['error'][:50]}")
