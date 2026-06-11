"""OpenRouter-based OCR service for handwritten text extraction."""

from __future__ import annotations

import base64
import io
import logging
from typing import TYPE_CHECKING, Any

import httpx

from src.core.config import get_settings

if TYPE_CHECKING:
    from PIL import Image

logger = logging.getLogger(__name__)


class OpenRouterOCRService:
    """Extract handwritten text from images using OpenRouter."""

    def __init__(self, api_key: str | None = None):
        settings = get_settings()
        self._api_key = api_key or settings.OPENROUTER_API_KEY
        self._model = "anthropic/claude-sonnet-4.6"
        self._base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def extract_text(self, image: Image.Image) -> dict[str, Any]:
        """
        Extract handwritten text from image.

        Args:
            image: PIL Image object

        Returns:
            {
                "text": str | None,
                "confidence": float,
                "model": str,
                "error": str | None
            }
        """
        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize to max 1024px to keep payload under OpenRouter limits
        max_size = 1024
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size))

        # Encode as JPEG (much smaller than PNG)
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        base64_image = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self._base_url,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "Computer Vision App",
                    },
                    json={
                        "model": self._model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}",
                                        },
                                    },
                                    {
                                        "type": "text",
                                        "text": (
                                            "Read all handwritten text in this image. "
                                            "Return ONLY the extracted text. "
                                            "If no handwriting found, return 'NO_HANDWRITING'."
                                        ),
                                    },
                                ],
                            }
                        ],
                        "max_tokens": 1000,
                    },
                )

                response.raise_for_status()
                data = response.json()
                if "choices" not in data:
                    error_msg = data.get("error", {}).get("message", str(data))
                    logger.error("OpenRouter unexpected response: %s", data)
                    return {
                        "text": None,
                        "confidence": 0.0,
                        "model": self._model,
                        "error": error_msg,
                    }
                extracted = data["choices"][0]["message"]["content"].strip()

                if extracted == "NO_HANDWRITING":
                    return {
                        "text": None,
                        "confidence": 1.0,
                        "model": self._model,
                        "error": None,
                    }

                return {
                    "text": extracted,
                    "confidence": 0.85,
                    "model": self._model,
                    "error": None,
                }

        except httpx.HTTPError as e:
            logger.error("OpenRouter API error: %s", e)
            return {
                "text": None,
                "confidence": 0.0,
                "model": self._model,
                "error": str(e),
            }
        except Exception as e:
            logger.error("Unexpected error during OCR extraction: %s", e)
            return {
                "text": None,
                "confidence": 0.0,
                "model": self._model,
                "error": str(e),
            }
