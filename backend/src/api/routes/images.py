"""Image routes for upload, retrieval, download, and deletion."""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.logging import get_logger
from ...db.session import get_db
from ...schemas.common import PaginatedResponse
from ...schemas.image import ImageResponse
from ...schemas.validation import ImageListParams
from ...services import ImageRepository, ImageService
from ...utils import FileStorage
from ..dependencies import validate_uploaded_image

router = APIRouter(prefix="/api/v1/images", tags=["images"])
logger = get_logger(__name__)


async def get_image_service(db: AsyncSession = Depends(get_db)) -> ImageService:
    repo = ImageRepository(db)
    storage = FileStorage()
    return ImageService(repository=repo, storage=storage)


@router.post(
    "/upload", response_model=ImageResponse, status_code=status.HTTP_201_CREATED
)
async def upload_image(
    file: UploadFile = Depends(validate_uploaded_image),
    original_url: str | None = None,
    service: ImageService = Depends(get_image_service),
):
    """Upload an image file and persist metadata.

    Following FastAPI best practices for file uploads and error handling.
    """
    content = await file.read()

    # Service layer now handles HTTPExceptions directly
    image = await service.upload_image(
        image_content=content,
        original_filename=file.filename or "uploaded_image",
        content_type=file.content_type or "application/octet-stream",
    )
    return image


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, service: ImageService = Depends(get_image_service)):
    """Retrieve image metadata by ID.

    Following FastAPI best practices - service layer handles errors.
    """
    # Service method now handles both UUID and int, and HTTPExceptions
    image = await service.get_image(image_id)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image {image_id} not found"
        )
    return image


@router.get("/", response_model=PaginatedResponse[ImageResponse])
async def list_images(
    params: ImageListParams = Depends(),
    service: ImageService = Depends(get_image_service),
):
    """List images with pagination and optional filters.

    Following FastAPI best practices - service layer handles validation and errors.
    """
    items, total = await service.get_paginated_images(
        page=params.page,
        page_size=params.page_size,
        status=params.status,
        filename_substr=params.filename_substr,
    )
    return PaginatedResponse[ImageResponse](
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


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
async def download_image_file(
    image_id: UUID, service: ImageService = Depends(get_image_service)
):
    """Download the original stored image file."""
    image = await service.get_image(image_id)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    storage = FileStorage()
    file_path = storage.get_file_path(image.storage_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File missing"
        )

    return FileResponse(
        path=str(file_path),
        media_type=_infer_media_type(file_path),
        filename=image.filename,
    )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: UUID, service: ImageService = Depends(get_image_service)
):
    """Delete image and its file."""
    ok = await service.delete_image(image_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )
    return None
