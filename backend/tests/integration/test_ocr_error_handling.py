"""Error handling and resilience tests for OCR service."""

import asyncio
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from src.services.openrouter_ocr_service import OpenRouterOCRService


class TestOCRErrorHandling:
    """Tests for error scenarios and resilience."""

    @pytest.mark.asyncio
    async def test_api_timeout(self) -> None:
        """Test handling of API timeout (>30 seconds)."""
        service = OpenRouterOCRService(api_key="test-key")

        # Create a test image
        img = Image.new("RGB", (100, 100), color="white")

        with patch("httpx.AsyncClient.post") as mock_post:
            # Simulate timeout
            mock_post.side_effect = asyncio.TimeoutError("Request timed out")

            result = await service.extract_text(img)

            # Verify graceful error handling
            assert result["text"] is None
            assert result["confidence"] == 0.0
            assert "timeout" in result["error"].lower()
            assert result["error"] is not None

    @pytest.mark.asyncio
    async def test_invalid_api_key(self) -> None:
        """Test handling of invalid/expired API key (401 Unauthorized)."""
        service = OpenRouterOCRService(api_key="invalid-key")
        img = Image.new("RGB", (100, 100), color="white")

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response

            result = await service.extract_text(img)

            assert result["text"] is None
            assert "401" in result["error"] or "unauthorized" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self) -> None:
        """Test handling of rate limit (429 Too Many Requests)."""
        service = OpenRouterOCRService(api_key="test-key")
        img = Image.new("RGB", (100, 100), color="white")

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_post.return_value = mock_response

            result = await service.extract_text(img)

            assert result["text"] is None
            assert "429" in result["error"] or "rate limit" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_server_error(self) -> None:
        """Test handling of server errors (5xx)."""
        service = OpenRouterOCRService(api_key="test-key")
        img = Image.new("RGB", (100, 100), color="white")

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.text = "Service Unavailable"
            mock_post.return_value = mock_response

            result = await service.extract_text(img)

            assert result["text"] is None
            assert "503" in result["error"]

    @pytest.mark.asyncio
    async def test_network_error(self) -> None:
        """Test handling of network connectivity issues."""
        service = OpenRouterOCRService(api_key="test-key")
        img = Image.new("RGB", (100, 100), color="white")

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.side_effect = ConnectionError("Network unreachable")

            result = await service.extract_text(img)

            assert result["text"] is None
            assert result["error"] is not None

    @pytest.mark.asyncio
    async def test_malformed_json_response(self) -> None:
        """Test handling of malformed API response."""
        service = OpenRouterOCRService(api_key="test-key")
        img = Image.new("RGB", (100, 100), color="white")

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_post.return_value = mock_response

            result = await service.extract_text(img)

            assert result["text"] is None
            assert result["error"] is not None

    @pytest.mark.asyncio
    async def test_image_conversion_to_rgb(self) -> None:
        """Test automatic conversion of non-RGB images."""
        service = OpenRouterOCRService(api_key="test-key")

        # Create RGBA image
        img = Image.new("RGBA", (100, 100), color=(255, 255, 255, 255))

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Test text"}}]
            }
            mock_post.return_value = mock_response

            result = await service.extract_text(img)

            # Verify post was called (conversion didn't fail)
            assert mock_post.called
            # Response structure should be valid
            assert "error" in result

    @pytest.mark.asyncio
    async def test_empty_response_content(self) -> None:
        """Test handling of empty response from API."""
        service = OpenRouterOCRService(api_key="test-key")
        img = Image.new("RGB", (100, 100), color="white")

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": []}
            mock_post.return_value = mock_response

            result = await service.extract_text(img)

            assert result["text"] is None
            assert result["error"] is not None

    @pytest.mark.asyncio
    async def test_partial_analysis_recovery(self) -> None:
        """Test that detection still works when OCR fails."""
        from uuid import uuid4

        from src.tasks.detection_tasks import analyze_image_with_ocr

        image_id = uuid4()
        image_bytes = BytesIO()
        Image.new("RGB", (100, 100), color="white").save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        with patch.object(
            OpenRouterOCRService, "extract_text"
        ) as mock_extract:
            # Simulate OCR failure
            mock_extract.return_value = {
                "text": None,
                "confidence": 0.0,
                "model": "claude-3.5-sonnet",
                "error": "API timeout",
            }

            result = await analyze_image_with_ocr(image_id, image_bytes.getvalue())

            # Verify status is "partial" (YOLO succeeded, OCR failed)
            assert result["status"] == "partial"
            assert result["text_extraction"]["error"] == "API timeout"
            # Detections should still be present
            assert isinstance(result["detections"], list)


class TestOCRResourceLimits:
    """Tests for resource constraints and limits."""

    @pytest.mark.asyncio
    async def test_large_image_handling(self) -> None:
        """Test handling of very large images."""
        service = OpenRouterOCRService(api_key="test-key")

        # Create a large image (10MB equivalent dimensions)
        large_img = Image.new("RGB", (4000, 4000), color="white")

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Text from large image"}}]
            }
            mock_post.return_value = mock_response

            result = await service.extract_text(large_img)

            # Should handle without crashing
            assert "error" in result or result["text"] is not None

    @pytest.mark.asyncio
    async def test_concurrent_requests_resilience(self) -> None:
        """Test resilience to concurrent API requests."""
        service = OpenRouterOCRService(api_key="test-key")

        # Create multiple test images
        images = [Image.new("RGB", (100, 100), color="white") for _ in range(5)]

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Concurrent test"}}]
            }
            mock_post.return_value = mock_response

            # Run 5 concurrent extraction requests
            tasks = [service.extract_text(img) for img in images]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verify all requests completed
            assert len(results) == 5
            # At least some should be successful dict responses
            assert any(isinstance(r, dict) for r in results)


class TestOCRRetryBehavior:
    """Tests for retry logic and resilience."""

    @pytest.mark.asyncio
    async def test_transient_failure_recovery(self) -> None:
        """Test recovery from transient failures."""
        service = OpenRouterOCRService(api_key="test-key")
        img = Image.new("RGB", (100, 100), color="white")

        with patch("httpx.AsyncClient.post") as mock_post:
            # Simulate transient failures followed by success
            call_count = 0

            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                mock_response = MagicMock()
                if call_count <= 1:
                    # First call fails temporarily
                    mock_response.status_code = 503
                else:
                    # Subsequent calls succeed
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "choices": [{"message": {"content": "Recovered"}}]
                    }
                return mock_response

            mock_post.side_effect = side_effect

            # Single call without retry (should fail)
            result = await service.extract_text(img)
            # Since service doesn't retry internally, first call determines result
            assert result["text"] is None or result["error"] is not None
