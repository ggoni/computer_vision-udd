"""Abstract repository interface for image persistence operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.models.image import Image


class ImageRepositoryInterface(ABC):
    """Repository abstraction for ``Image`` entities."""

    @abstractmethod
    async def create(self, image_data: dict) -> Image:
        """Persist a new image record and return the created ORM instance."""

    @abstractmethod
    async def get_by_id(self, image_id: UUID) -> Image | None:
        """Retrieve an image by its identifier, returning ``None`` when missing."""

    @abstractmethod
    async def update_status(self, image_id: UUID, status: str) -> Image:
        """Update the status of an image and return the updated instance."""

    @abstractmethod
    async def delete(self, image_id: UUID) -> bool:
        """Delete an image record and return ``True`` when a row was removed."""
