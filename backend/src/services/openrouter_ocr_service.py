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
        self._model = "claude-3.5-sonnet"
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

        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
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
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": base64_image,
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
