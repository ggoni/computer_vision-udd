"""SQLAlchemy implementation of the image repository."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def get_by_id(self, image_id: UUID) -> Image | None:
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

    async def get_paginated(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        filename_substr: str | None = None,
    ) -> tuple[list[Image], int]:
        """Return a page of images and total count with optional filters.

        Ordered by upload timestamp desc, then created_at desc.
        """
        if page <= 0 or page_size <= 0:
            return ([], 0)

        stmt = select(Image)
        if status:
            stmt = stmt.where(Image.status == status)
        if filename_substr:
            like_pattern = f"%{filename_substr}%"
            stmt = stmt.where(Image.filename.ilike(like_pattern))

        count_stmt = stmt.with_only_columns(func.count()).order_by(None)
        total = (await self._session.execute(count_stmt)).scalar_one()

        page_stmt = (
            stmt.order_by(Image.upload_timestamp.desc(), Image.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(page_stmt)
        items = list(result.scalars().all())
        return (items, total)
