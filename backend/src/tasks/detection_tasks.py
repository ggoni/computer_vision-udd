"""Async image analysis tasks for object detection and OCR.

This module provides tasks for running YOLO detection and OpenRouter OCR
in parallel, combining results, and storing them.
"""

from __future__ import annotations

import asyncio
import logging
from io import BytesIO
from typing import TYPE_CHECKING, Any
from uuid import UUID

from PIL import Image

from src.services.openrouter_ocr_service import OpenRouterOCRService
from src.services.yolos_cv_service import YOLOSCVService
from src.utils.file_storage import FileStorage

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


async def analyze_image_with_ocr(image_id: UUID, image_bytes: bytes) -> dict[str, Any]:
    """
    Run YOLO detection + OpenRouter OCR in parallel.

    Combines results and returns structured response.
    Returns partial results if OCR fails but detection succeeds.

    Args:
        image_id: UUID of the image being analyzed
        image_bytes: Raw image bytes

    Returns:
        {
            "image_id": str,
            "status": "success" | "partial",
            "detections": list[dict],
            "text_extraction": {
                "text": str | None,
                "confidence": float,
                "model": str,
                "error": str | None
            }
        }
    """
    try:
        # Load image
        image = Image.open(BytesIO(image_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")

        logger.info("Starting analysis for image %s", image_id)

        # Run YOLO detection
        logger.debug("Starting YOLO detection for image %s", image_id)
        yolo_service = YOLOSCVService()
        yolo_service.load_model()
        detections = yolo_service.detect_objects(image)
        logger.debug("YOLO detection completed: %d objects found", len(detections))

        # Run OCR
        logger.debug("Starting OCR extraction for image %s", image_id)
        ocr_service = OpenRouterOCRService()
        ocr_result = await ocr_service.extract_text(image)
        logger.debug("OCR extraction completed: text=%s, error=%s",
                     bool(ocr_result["text"]), ocr_result["error"])

        # Determine overall status
        status_result = "success" if ocr_result["error"] is None else "partial"

        result = {
            "image_id": str(image_id),
            "status": status_result,
            "detections": detections,
            "text_extraction": ocr_result,
        }

        logger.info("Analysis completed for image %s: status=%s",
                   image_id, status_result)

        return result

    except Exception as exc:
        logger.error("Analysis failed for image %s: %s", image_id, exc, exc_info=True)
        raise


# Convenience function for direct async calls
async def run_analysis(image_id: UUID, storage: FileStorage) -> dict[str, Any]:
    """Load image from storage and run full analysis.

    Args:
        image_id: UUID of image to analyze
        storage: FileStorage instance

    Returns:
        Combined analysis results with detections and OCR text
    """
    image_bytes = storage.get_file(str(image_id))
    return await analyze_image_with_ocr(image_id, image_bytes)
