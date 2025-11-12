"""Image routes for upload, retrieval, download, and deletion."""

from __future__ import annotations

from typing import Optional
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
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


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: UUID, service: ImageService = Depends(get_image_service)):
    """Retrieve image metadata by ID."""
    image = await service.get_image(image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return image


def _infer_media_type(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
    }.get(ext, "application/octet-stream")


@router.get("/{image_id}/file")
async def download_image_file(image_id: UUID, service: ImageService = Depends(get_image_service)):
    """Download the original stored image file."""
    image = await service.get_image(image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    storage = FileStorage()
    file_path = storage.get_file_path(image.storage_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing")

    return FileResponse(
        path=str(file_path),
        media_type=_infer_media_type(file_path),
        filename=image.filename,
    )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: UUID, service: ImageService = Depends(get_image_service)):
    """Delete image and its file."""
    ok = await service.delete_image(image_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return None
