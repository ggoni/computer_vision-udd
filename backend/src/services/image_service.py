"""Image service orchestrating file storage and repository operations.

This service applies business rules for handling uploaded images, including
validation, persistence to storage, and database record management.
"""

from __future__ import annotations

import logging
from uuid import UUID

from ..core.config import get_settings
from ..schemas.image import ImageInDB
from ..utils import FileStorage, validate_file_extension, validate_file_size
from .image_repository import ImageRepositoryInterface

logger = logging.getLogger(__name__)


class ImageService:
    """Service layer for image-related operations."""

    def __init__(
        self,
        repository: ImageRepositoryInterface,
        storage: FileStorage | None = None,
    ) -> None:
        self._repo = repository
        self._storage = storage or FileStorage()
        self._settings = get_settings()

    async def save_uploaded_image(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        original_url: str | None = None,
    ) -> ImageInDB:
        """Validate and persist an uploaded image.

        Steps:
        - Validate filename extension and size limits
        - Save file to storage (organized path)
        - Create Image record in repository
        - Return ImageInDB schema
        """

        if not filename:
            raise ValueError("Filename is required")

        # Validate extension
        if not validate_file_extension(filename):
            raise ValueError("Unsupported file type. Allowed: .jpg, .jpeg, .png, .webp")

        # Validate size
        file_size = len(file_bytes) if file_bytes is not None else 0
        if not validate_file_size(file_size, self._settings.MAX_UPLOAD_SIZE):
            raise ValueError(
                f"File size must be between 1 and {self._settings.MAX_UPLOAD_SIZE} bytes"
            )

        # Save file to storage
        try:
            storage_path = self._storage.save_file(file_bytes, filename)
        except Exception as exc:  # pragma: no cover - relies on filesystem errors
            logger.error("Failed to save file to storage: %s", exc)
            raise

        # Persist DB record via repository
        image_data = {
            "filename": filename,
            "original_url": original_url,
            "storage_path": storage_path,
            "file_size": file_size,
            # status and timestamps handled by model defaults/DB
        }

        image = await self._repo.create(image_data)

        # Map to schema
        return ImageInDB.model_validate(image)

    async def get_image(self, image_id: UUID) -> ImageInDB | None:
        """Retrieve an image by id and map to schema."""
        image = await self._repo.get_by_id(image_id)
        if image is None:
            return None
        return ImageInDB.model_validate(image)

    async def delete_image(self, image_id: UUID) -> bool:
        """Delete image from storage and repository.

        Order of operations:
        1) Fetch image to get storage path
        2) Attempt storage deletion (best-effort; proceed even if file is missing)
        3) Delete DB record; success is determined by DB deletion
        """

        image = await self._repo.get_by_id(image_id)
        if image is None:
            return False

        # Try to remove file from storage (do not fail the whole operation if file missing)
        try:
            self._storage.delete_file(image.storage_path)
        except Exception as exc:  # pragma: no cover - depends on filesystem issues
            logger.warning("Failed to delete file from storage: %s", exc)

        # Remove DB record
        return await self._repo.delete(image_id)

    async def get_paginated_images(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        filename_substr: str | None = None,
    ) -> tuple[list[ImageInDB], int]:
        """Return paginated images mapped to schemas with total count.

        Applies optional filters and delegates to repository.
        """
        items, total = await self._repo.get_paginated(
            page=page,
            page_size=page_size,
            status=status,
            filename_substr=filename_substr,
        )
        mapped = [ImageInDB.model_validate(img) for img in items]
        return (mapped, total)
