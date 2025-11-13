"""Image service orchestrating file storage and repository operations.

Provides business logic layer with comprehensive error handling and validation.
"""

import logging
from typing import BinaryIO
from uuid import UUID

from fastapi import HTTPException, status
from ..schemas.image import ImageInDB
from .image_repository_impl import ImageRepository
from ..utils.file_storage import FileStorage

logger = logging.getLogger(__name__)


class ImageService:
    """Service layer for image-related operations."""

    def __init__(
        self,
        repository: ImageRepository,
        storage: FileStorage | None = None,
    ):
        self._repo = repository
        self._storage = storage or FileStorage()

    async def save_uploaded_image(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        original_url: str | None = None,
    ) -> ImageInDB:
        """Save uploaded image - compatibility method.

        Maintains interface compatibility while using FastAPI patterns.
        """
        return await self.upload_image(
            image_content=file_bytes,
            original_filename=filename,
            content_type="application/octet-stream",
        )

    async def upload_image(
        self,
        *,
        image_content: bytes,
        original_filename: str,
        content_type: str,
    ) -> ImageInDB:
        """Validate and persist an uploaded image.

        Args:
            image_content: Binary image data (bytes)
            original_filename: Original filename from upload
            content_type: MIME type of the image

        Returns:
            ImageInDB: Created image record

        Raises:
            HTTPException: If validation fails or storage error occurs
        """
        try:
            # Save file to storage (FileStorage.save_file is synchronous)
            stored_path = self._storage.save_file(
                image_content, original_filename
            )

            # Get file size from saved bytes
            file_size = len(image_content)

            # Create database record
            image_record = await self._repo.create({
                "filename": original_filename,
                "storage_path": stored_path,
                "file_size": file_size,
                "status": "pending",
            })

            return ImageInDB.model_validate(image_record)

        except ValueError as e:
            logger.error("Image validation failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image: {e}"
            )
        except Exception as e:
            logger.error("Failed to upload image: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Image upload failed"
            )

    async def get_image(self, image_id: UUID | int | str) -> ImageInDB | None:
        """Get image by ID (supports UUID, int, or str)."""
        try:
            # Convert to UUID if needed
            if isinstance(image_id, int):
                # System uses UUIDs, can't convert int to UUID directly
                # This path shouldn't be used, but handle it gracefully
                raise ValueError(f"Invalid image ID type: {type(image_id)}")
            elif isinstance(image_id, str):
                from uuid import UUID as UUIDType
                image_id = UUIDType(image_id)

            image = await self._repo.get_by_id(image_id)
            return ImageInDB.model_validate(image) if image else None
        except ValueError as e:
            logger.error("Invalid image ID %s: %s", image_id, e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image ID: {e}"
            )
        except Exception as e:
            logger.error("Failed to retrieve image %s: %s", image_id, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve image"
            )

    async def delete_image(self, image_id: UUID | int | str) -> bool:
        """Delete image from storage and repository.

        Args:
            image_id: ID of image to delete (UUID, int, or str)

        Returns:
            bool: True if deletion successful

        Raises:
            HTTPException: If image not found or deletion fails
        """
        try:
            # Convert to UUID if needed
            if isinstance(image_id, int):
                raise ValueError(f"Invalid image ID type: {type(image_id)}")
            elif isinstance(image_id, str):
                from uuid import UUID as UUIDType
                image_id = UUIDType(image_id)

            # Get image details first
            image = await self._repo.get_by_id(image_id)
            if not image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Image {image_id} not found"
                )

            # Delete from storage and database
            self._storage.delete_file(image.storage_path)
            result = await self._repo.delete(image_id)

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete image"
                )

            return result

        except HTTPException:
            raise
        except ValueError as e:
            logger.error("Invalid image ID %s: %s", image_id, e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image ID: {e}"
            )
        except Exception as e:
            logger.error("Failed to delete image %s: %s", image_id, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Image deletion failed"
            )

    async def get_paginated_images(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        filename_substr: str | None = None,
    ) -> tuple[list[ImageInDB], int]:
        """Return paginated images mapped to schemas with total count.

        Applies optional filters and delegates to repository following
        FastAPI best practices for pagination and error handling.
        
        Args:
            page: Page number (1-based)
            page_size: Number of items per page (1-200)
            status: Optional filter by image status (pending, completed, failed)
            filename_substr: Optional filter by filename substring (case-insensitive)
            
        Returns:
            tuple: (list of ImageInDB objects, total count)
            
        Raises:
            HTTPException: If validation fails or database error occurs
        """
        # Input validation following FastAPI patterns
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be >= 1"
            )
        if page_size < 1 or page_size > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size must be between 1 and 200"
            )
            
        try:
            items, total = await self._repo.get_paginated(
                page=page,
                page_size=page_size,
                status=status,
                filename_substr=filename_substr,
            )
            mapped = [ImageInDB.model_validate(img) for img in items]
            return (mapped, total)
        except Exception as e:
            logger.error("Failed to retrieve paginated images: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve images"
            )
