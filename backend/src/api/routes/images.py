"""Image routes for upload, retrieval, download, and deletion."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_db
from ...schemas.image import ImageResponse
from ...services import ImageRepository, ImageService
from ...utils import FileStorage
from ..dependencies import validate_uploaded_image


router = APIRouter(prefix="/api/v1/images", tags=["images"])


async def get_image_service(db: AsyncSession = Depends(get_db)) -> ImageService:
    repo = ImageRepository(db)
    storage = FileStorage()
    return ImageService(repository=repo, storage=storage)


@router.post("/upload", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = Depends(validate_uploaded_image),
    original_url: Optional[str] = None,
    service: ImageService = Depends(get_image_service),
):
    """Upload an image file and persist metadata."""
    content = await file.read()
    try:
        image = await service.save_uploaded_image(
            file_bytes=content,
            filename=file.filename or "uploaded_image",
            original_url=original_url,
        )
        return image
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))
