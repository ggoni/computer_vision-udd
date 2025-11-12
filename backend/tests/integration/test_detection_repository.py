"""Integration tests for DetectionRepository."""

from __future__ import annotations

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.detection_repository import DetectionRepository
from src.services.image_repository_impl import ImageRepository
from src.models.detection import Detection
from src.models.image import Image
from src.db.session import get_session_local


@pytest_asyncio.fixture
async def db_session():
    session_factory = get_session_local()
    async with session_factory() as session:
        yield session
        await session.rollback()


async def _create_image(repo: ImageRepository) -> Image:
    data = {
        "filename": "det.jpg",
        "storage_path": "uploads/det.jpg",
        "file_size": 1234,
        "status": "pending",
        "upload_timestamp": datetime.now(timezone.utc),
    }
    return await repo.create(data)


@pytest.mark.asyncio
async def test_create_many_inserts_all_detections(db_session: AsyncSession):
    img_repo = ImageRepository(db_session)
    img = await _create_image(img_repo)

    repo = DetectionRepository(db_session)
    dets = [
        {
            "image_id": img.id,
            "label": "cat",
            "confidence_score": 0.95,
            "bbox_xmin": 10,
            "bbox_ymin": 10,
            "bbox_xmax": 50,
            "bbox_ymax": 60,
        },
        {
            "image_id": img.id,
            "label": "dog",
            "confidence_score": 0.88,
            "bbox_xmin": 20,
            "bbox_ymin": 20,
            "bbox_xmax": 70,
            "bbox_ymax": 80,
        },
    ]

    created = await repo.create_many(dets)
    assert len(created) == 2
    assert all(isinstance(d, Detection) for d in created)


@pytest.mark.asyncio
async def test_get_by_image_id_orders_by_confidence(db_session: AsyncSession):
    img_repo = ImageRepository(db_session)
    img = await _create_image(img_repo)
    repo = DetectionRepository(db_session)

    await repo.create_many([
        {"image_id": img.id, "label": "a", "confidence_score": 0.50, "bbox_xmin": 1, "bbox_ymin": 1, "bbox_xmax": 2, "bbox_ymax": 2},
        {"image_id": img.id, "label": "b", "confidence_score": 0.90, "bbox_xmin": 1, "bbox_ymin": 1, "bbox_xmax": 2, "bbox_ymax": 2},
        {"image_id": img.id, "label": "c", "confidence_score": 0.75, "bbox_xmin": 1, "bbox_ymin": 1, "bbox_xmax": 2, "bbox_ymax": 2},
    ])

    rows = await repo.get_by_image_id(img.id)
    scores = [r.confidence_score for r in rows]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_get_paginated_with_filters(db_session: AsyncSession):
    img_repo = ImageRepository(db_session)
    img = await _create_image(img_repo)
    repo = DetectionRepository(db_session)

    # 5 cats (two above 0.9), 5 dogs
    dets = []
    for i in range(5):
        dets.append({"image_id": img.id, "label": "cat", "confidence_score": 0.91 if i < 2 else 0.5 + i*0.05, "bbox_xmin": i, "bbox_ymin": i, "bbox_xmax": i+1, "bbox_ymax": i+1})
        dets.append({"image_id": img.id, "label": "dog", "confidence_score": 0.4 + i*0.1, "bbox_xmin": i, "bbox_ymin": i, "bbox_xmax": i+1, "bbox_ymax": i+1})
    await repo.create_many(dets)

    items, total = await repo.get_paginated(page=1, page_size=10, label="cat", min_confidence=0.9)
    assert total >= 2
    assert all(it.label == "cat" and it.confidence_score >= 0.9 for it in items)

    # Page 2 should be empty for these filters
    items2, total2 = await repo.get_paginated(page=2, page_size=10, label="cat", min_confidence=0.9)
    assert total2 == total
    assert len(items2) == 0


@pytest.mark.asyncio
async def test_delete_by_image_id(db_session: AsyncSession):
    img_repo = ImageRepository(db_session)
    img = await _create_image(img_repo)
    repo = DetectionRepository(db_session)

    await repo.create_many([
        {"image_id": img.id, "label": "x", "confidence_score": 0.5, "bbox_xmin": 0, "bbox_ymin": 0, "bbox_xmax": 1, "bbox_ymax": 1},
        {"image_id": img.id, "label": "y", "confidence_score": 0.6, "bbox_xmin": 0, "bbox_ymin": 0, "bbox_xmax": 1, "bbox_ymax": 1},
    ])

    deleted = await repo.delete_by_image_id(img.id)
    assert deleted >= 2

    remaining = await repo.get_by_image_id(img.id)
    assert remaining == []
