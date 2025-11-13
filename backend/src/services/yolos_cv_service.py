"""YOLOS-based computer vision service implementation."""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Any

from PIL import Image

from src.core.config import get_settings
from src.services.cv_service_interface import CVServiceInterface
from src.utils import ModelLoader

logger = logging.getLogger(__name__)


class YOLOSCVService(CVServiceInterface):
    """Concrete computer vision service using Hugging Face YOLOS models."""

    def __init__(
        self,
        model_loader: ModelLoader | None = None,
        *,
        confidence_threshold: float | None = None,
    ) -> None:
        settings = get_settings()
        self._model_loader = model_loader or ModelLoader()
        self._confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else settings.CONFIDENCE_THRESHOLD
        )
        self._model_name = settings.MODEL_NAME

    def load_model(self) -> None:
        """Load the detection model and warm it up."""
        logger.info("Loading YOLOS model '%s'", self._model_name)
        start = perf_counter()
        self._model_loader.load_model()
        duration = perf_counter() - start
        logger.info("Model loaded in %.2fs", duration)

        try:
            self._model_loader.warmup()
        except (
            Exception
        ) as exc:  # pragma: no cover - warmup failures should not break startup
            logger.warning("Model warmup failed: %s", exc)

    def detect_objects(self, image: Image.Image) -> list[dict[str, Any]]:
        """Run object detection on the provided image."""
        if image.mode != "RGB":
            image = image.convert("RGB")

        model = self._model_loader.get_model()

        start = perf_counter()
        raw_results = model(image)
        inference_time = perf_counter() - start
        logger.debug(
            "YOLOS inference produced %d raw detections in %.3fs",
            len(raw_results),
            inference_time,
        )

        detections: list[dict[str, Any]] = []
        for item in raw_results:
            score = float(item.get("score") or item.get("confidence", 0.0))
            if score < self._confidence_threshold:
                continue

            box = item.get("box") or {}
            detections.append(
                {
                    "label": item.get("label", "unknown"),
                    "confidence_score": score,
                    "bbox": {
                        "xmin": int(round(box.get("xmin", box.get("x", 0)))),
                        "ymin": int(round(box.get("ymin", box.get("y", 0)))),
                        "xmax": int(
                            round(box.get("xmax", box.get("x", 0) + box.get("w", 0)))
                        ),
                        "ymax": int(
                            round(box.get("ymax", box.get("y", 0) + box.get("h", 0)))
                        ),
                    },
                }
            )

        detections.sort(key=lambda det: det["confidence_score"], reverse=True)
        logger.debug("Returning %d detections after filtering", len(detections))
        return detections
