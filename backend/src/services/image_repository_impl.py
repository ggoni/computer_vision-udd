"""SQLAlchemy implementation of the image repository."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.image import Image
from src.services.image_repository import ImageRepositoryInterface

logger = logging.getLogger(__name__)


class ImageRepository(ImageRepositoryInterface):
    """Concrete repository for ``Image`` entities using SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, image_data: dict) -> Image:
        image = Image(**image_data)
        self._session.add(image)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.error("Failed to create image due to integrity error: %s", exc)
            raise ValueError("Image with the same attributes already exists") from exc

        await self._session.refresh(image)
        return image

    async def get_by_id(self, image_id: UUID) -> Optional[Image]:
        stmt = select(Image).where(Image.id == image_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, image_id: UUID, status: str) -> Image:
        stmt = select(Image).where(Image.id == image_id).with_for_update()
        result = await self._session.execute(stmt)
        image = result.scalar_one_or_none()
        if image is None:
            raise ValueError("Image not found")

        image.status = status
        await self._session.flush()
        await self._session.refresh(image)
        return image

    async def delete(self, image_id: UUID) -> bool:
        stmt = select(Image).where(Image.id == image_id)
        result = await self._session.execute(stmt)
        image = result.scalar_one_or_none()
        if image is None:
            return False

        await self._session.delete(image)
        await self._session.flush()
        return True
