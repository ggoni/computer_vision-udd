"""Detection service orchestrating CV inference and persistence."""

from __future__ import annotations

import logging
from uuid import UUID

from PIL import Image

from src.schemas.common import PaginatedResponse
from src.schemas.detection import DetectionResponse
from src.services.cv_service_interface import CVServiceInterface
from src.services.detection_repository import DetectionRepository
from src.services.image_repository_impl import ImageRepository
from src.utils import FileStorage, preprocess_image

logger = logging.getLogger(__name__)


class DetectionService:
    """Service layer for detection-related operations."""

    def __init__(
        self,
        *,
        detection_repo: DetectionRepository,
        cv_service: CVServiceInterface,
        image_repo: ImageRepository,
        storage: FileStorage | None = None,
    ) -> None:
        self._det_repo = detection_repo
        self._cv = cv_service
        self._img_repo = image_repo
        self._storage = storage or FileStorage()

    async def analyze_image(self, image_id: UUID) -> list[DetectionResponse]:
        """Run CV analysis for an image and persist detections.

        Returns list of DetectionResponse.
        """
        image = await self._img_repo.get_by_id(image_id)
        if image is None:
            raise ValueError("Image not found")

        # Load and preprocess image
        file_path = self._storage.get_file_path(image.storage_path)
        img_bytes = file_path.read_bytes()
        pil_img: Image.Image = preprocess_image(img_bytes)

        # Run CV
        raw = self._cv.detect_objects(pil_img)

        # Map to repo format
        to_create = []
        for d in raw:
            bbox = d.get("bbox", {})
            to_create.append(
                {
                    "image_id": image.id,
                    "label": d.get("label", "unknown"),
                    "confidence_score": float(
                        d.get("confidence_score", d.get("score", 0.0))
                    ),
                    "bbox_xmin": int(bbox.get("xmin", 0)),
                    "bbox_ymin": int(bbox.get("ymin", 0)),
                    "bbox_xmax": int(bbox.get("xmax", 0)),
                    "bbox_ymax": int(bbox.get("ymax", 0)),
                }
            )

        created = await self._det_repo.create_many(to_create) if to_create else []

        # Update image status
        await self._img_repo.update_status(image.id, "completed")

        return [DetectionResponse.model_validate(x) for x in created]

    async def get_detections(self, image_id: UUID) -> list[DetectionResponse]:
        rows = await self._det_repo.get_by_image_id(image_id)
        return [DetectionResponse.model_validate(x) for x in rows]

    async def get_all_paginated(
        self,
        *,
        page: int,
        page_size: int,
        label: str | None = None,
        min_confidence: float | None = None,
    ) -> PaginatedResponse[DetectionResponse]:
        items, total = await self._det_repo.get_paginated(
            page=page, page_size=page_size, label=label, min_confidence=min_confidence
        )
        mapped = [DetectionResponse.model_validate(x) for x in items]
        return PaginatedResponse[DetectionResponse](
            items=mapped, total=total, page=page, page_size=page_size
        )
