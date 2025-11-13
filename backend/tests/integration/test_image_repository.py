"""Integration tests for ImageRepository."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
import pytest_asyncio

from src.db.session import get_session_local
from src.models.image import Image
from src.services.image_repository_impl import ImageRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def db_session():
    session_factory = get_session_local()
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_create_image(db_session: AsyncSession):
    repo = ImageRepository(db_session)
    image_data = {
        "filename": "test.jpg",
        "storage_path": "uploads/test.jpg",
        "file_size": 1024,
        "status": "pending",
        "upload_timestamp": datetime.now(UTC),
    }

    image = await repo.create(image_data)

    assert isinstance(image, Image)
    assert image.id is not None
    assert image.filename == "test.jpg"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_if_missing(db_session: AsyncSession):
    repo = ImageRepository(db_session)

    result = await repo.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_update_status(db_session: AsyncSession):
    repo = ImageRepository(db_session)
    image_data = {
        "filename": "status.jpg",
        "storage_path": "uploads/status.jpg",
        "file_size": 2048,
        "status": "pending",
        "upload_timestamp": datetime.now(UTC),
    }
    image = await repo.create(image_data)

    updated = await repo.update_status(image.id, "completed")

    assert updated.status == "completed"


@pytest.mark.asyncio
async def test_delete_image(db_session: AsyncSession):
    repo = ImageRepository(db_session)
    image_data = {
        "filename": "delete.jpg",
        "storage_path": "uploads/delete.jpg",
        "file_size": 512,
        "status": "pending",
        "upload_timestamp": datetime.now(UTC),
    }
    image = await repo.create(image_data)

    deleted = await repo.delete(image.id)

    assert deleted is True
    assert await repo.get_by_id(image.id) is None
