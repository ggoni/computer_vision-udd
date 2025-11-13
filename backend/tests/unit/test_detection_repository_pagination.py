"""Unit tests for DetectionRepository pagination edge cases."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from src.db.session import get_session_local
from src.models.detection import Detection
from src.models.image import Image
from src.services.detection_repository import DetectionRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def db_session():
    """Database session with automatic rollback for test isolation."""
    session_factory = get_session_local()
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_pagination_invalid_page_or_size_returns_empty(db_session: AsyncSession):
    repo = DetectionRepository(db_session)
    items, total = await repo.get_paginated(page=0, page_size=10)
    assert items == [] and total == 0
    items2, total2 = await repo.get_paginated(page=1, page_size=0)
    assert items2 == [] and total2 == 0


@pytest.mark.asyncio
async def test_pagination_with_filters(db_session: AsyncSession):
    # Create image
    image = Image(
        filename="repo_test.jpg",
        storage_path="2025/11/12/repo_test.jpg",
        file_size=100,
        status="completed",
        upload_timestamp=datetime.now(UTC),
    )
    db_session.add(image)
    await db_session.flush()
    await db_session.refresh(image)

    # Create detections with varying confidence and labels
    d1 = Detection(
        image_id=image.id,
        label="cat",
        confidence_score=0.9,
        bbox_xmin=0,
        bbox_ymin=0,
        bbox_xmax=10,
        bbox_ymax=10,
    )
    d2 = Detection(
        image_id=image.id,
        label="dog",
        confidence_score=0.5,
        bbox_xmin=1,
        bbox_ymin=1,
        bbox_xmax=11,
        bbox_ymax=11,
    )
    d3 = Detection(
        image_id=image.id,
        label="cat",
        confidence_score=0.3,
        bbox_xmin=2,
        bbox_ymin=2,
        bbox_xmax=12,
        bbox_ymax=12,
    )
    db_session.add_all([d1, d2, d3])
    await db_session.flush()

    repo = DetectionRepository(db_session)

    # Filter by label
    cat_items, cat_total = await repo.get_paginated(
        page=1, page_size=10, label="cat"
    )
    assert cat_total >= 2  # At least the 2 cats we created
    assert all(d.label == "cat" for d in cat_items)

    # Filter by min_confidence
    conf_items, conf_total = await repo.get_paginated(
        page=1, page_size=10, min_confidence=0.6
    )
    assert conf_total >= 1  # At least the 1 detection with confidence >= 0.6
    assert all(d.confidence_score >= 0.6 for d in conf_items)

    # Combined filter
    combo_items, combo_total = await repo.get_paginated(
        page=1, page_size=10, label="cat", min_confidence=0.8
    )
    assert combo_total >= 1  # At least 1 cat with confidence >= 0.8
    assert all(item.label == "cat" and item.confidence_score >= 0.8 for item in combo_items)
