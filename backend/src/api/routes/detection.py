"""Detection routes for analyzing images and listing detections."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_db
from ...schemas.common import PaginatedResponse
from ...schemas.detection import DetectionResponse
from ...services import DetectionRepository, DetectionService, ImageRepository
from ...services.yolos_cv_service import YOLOSCVService
from ...utils import FileStorage

router = APIRouter(prefix="/api/v1", tags=["detections"])


async def get_detection_service(db: AsyncSession = Depends(get_db)) -> DetectionService:
    det_repo = DetectionRepository(db)
    img_repo = ImageRepository(db)
    cv = YOLOSCVService()  # Real CV service; can be overridden in tests
    storage = FileStorage()
    return DetectionService(
        detection_repo=det_repo, cv_service=cv, image_repo=img_repo, storage=storage
    )


@router.post(
    "/images/{image_id}/analyze",
    response_model=list[DetectionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def analyze_image(
    image_id: UUID, service: DetectionService = Depends(get_detection_service)
):
    """Run object detection on an uploaded image.

    Returns list of detections. Updates image status to 'completed'.
    """
    try:
        detections = await service.analyze_image(image_id)
        return detections
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/images/{image_id}/detections", response_model=list[DetectionResponse])
async def list_image_detections(
    image_id: UUID, service: DetectionService = Depends(get_detection_service)
):
    """List detections for a specific image."""
    detections = await service.get_detections(image_id)
    return detections


@router.get("/detections", response_model=PaginatedResponse[DetectionResponse])
async def list_detections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    label: str | None = Query(None, min_length=1),
    min_confidence: float | None = Query(None, ge=0.0, le=1.0),
    service: DetectionService = Depends(get_detection_service),
):
    """List detections globally with pagination and optional filters."""
    return await service.get_all_paginated(
        page=page, page_size=page_size, label=label, min_confidence=min_confidence
    )
