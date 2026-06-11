"""OpenRouter-based OCR and classification service using Gemini."""

from __future__ import annotations

import base64
import io
import json
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
        self._model = "google/gemini-2.5-flash"
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
        base64_image = self._encode_image(image)

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

    def _encode_image(self, image: Image.Image) -> str:
        """Encode a PIL image to a base64 JPEG string."""
        if image.mode != "RGB":
            image = image.convert("RGB")
        max_size = 1024
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

    async def classify_objects(self, image: Image.Image) -> dict[str, Any]:
        """
        Classify the main objects visible in an image using Gemini.

        Returns:
            {
                "objects": [{"label": str, "confidence": float}, ...],
                "model": str,
                "error": str | None,
            }
        """
        base64_image = self._encode_image(image)
        prompt = (
            "List every distinct object, animal, or person visible in this image. "
            "Respond ONLY with a JSON array, no markdown fences. Example: "
            '[{"label": "llama", "confidence": 0.97}, {"label": "mountain", "confidence": 0.85}]. '
            "Be specific (e.g. 'llama' not 'animal'). "
            "Use English labels."
        )
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
                                    {"type": "text", "text": prompt},
                                ],
                            }
                        ],
                        "max_tokens": 500,
                    },
                )
                response.raise_for_status()
                data = response.json()

                if "choices" not in data:
                    error_msg = data.get("error", {}).get("message", str(data))
                    logger.error("OpenRouter classification unexpected response: %s", data)
                    return {"objects": [], "model": self._model, "error": error_msg}

                raw = data["choices"][0]["message"]["content"].strip()
                objects = json.loads(raw)
                if not isinstance(objects, list):
                    raise ValueError("Expected a JSON array")
                return {"objects": objects, "model": self._model, "error": None}

        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Failed to parse classification response: %s", e)
            return {"objects": [], "model": self._model, "error": f"parse error: {e}"}
        except httpx.HTTPError as e:
            logger.error("OpenRouter classification API error: %s", e)
            return {"objects": [], "model": self._model, "error": str(e)}
        except Exception as e:
            logger.error("Unexpected error during classification: %s", e)
            return {"objects": [], "model": self._model, "error": str(e)}
