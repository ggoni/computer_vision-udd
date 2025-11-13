from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
import pytest_asyncio
from PIL import Image

from src.services.detection_service import DetectionService


class DummyImage:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest_asyncio.fixture
async def mock_cv():
    cv = Mock()
    cv.detect_objects.return_value = [
        {
            "label": "cat",
            "confidence_score": 0.95,
            "bbox": {"xmin": 1, "ymin": 2, "xmax": 10, "ymax": 12},
        },
        {
            "label": "dog",
            "confidence_score": 0.5,
            "bbox": {"xmin": 3, "ymin": 4, "xmax": 8, "ymax": 9},
        },
    ]
    return cv


@pytest_asyncio.fixture
async def mock_repos():
    det_repo = Mock()
    det_repo.create_many = AsyncMock()
    det_repo.get_by_image_id = AsyncMock()
    det_repo.get_paginated = AsyncMock()

    img_repo = Mock()
    img_repo.get_by_id = AsyncMock()
    img_repo.update_status = AsyncMock()

    return det_repo, img_repo


@pytest_asyncio.fixture
async def storage_and_tmpfile(tmp_path):
    # Create a small valid image file
    p = tmp_path / "img.jpg"
    img = Image.new("RGB", (16, 16), color=(255, 0, 0))
    img.save(p, format="JPEG")

    storage = Mock()
    storage.get_file_path.return_value = p
    return storage


@pytest.mark.asyncio
async def test_analyze_image_orchestrates_workflow(
    mock_cv, mock_repos, storage_and_tmpfile, monkeypatch
):
    det_repo, img_repo = mock_repos

    image_id = uuid4()
    img_repo.get_by_id.return_value = DummyImage(
        id=image_id,
        storage_path="any",
    )

    # Bypass preprocess_image by using the actual file and a simple identity
    from src.services import detection_service as ds_mod

    monkeypatch.setattr(
        ds_mod,
        "preprocess_image",
        lambda b: Image.open(storage_and_tmpfile.get_file_path("")),
    )

    det_repo.create_many.return_value = [
        DummyImage(
            id=uuid4(),
            image_id=image_id,
            label="cat",
            confidence_score=0.95,
            bbox_xmin=1,
            bbox_ymin=2,
            bbox_xmax=10,
            bbox_ymax=12,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    ]

    service = DetectionService(
        detection_repo=det_repo,
        cv_service=mock_cv,
        image_repo=img_repo,
        storage=storage_and_tmpfile,
    )

    results = await service.analyze_image(image_id)
    assert len(results) == 1
    img_repo.update_status.assert_called_once_with(image_id, "completed")
    det_repo.create_many.assert_called_once()


@pytest.mark.asyncio
async def test_get_detections_returns_mapped(mock_cv, mock_repos):
    det_repo, img_repo = mock_repos
    image_id = uuid4()

    det_repo.get_by_image_id.return_value = [
        DummyImage(
            id=uuid4(),
            image_id=image_id,
            label="x",
            confidence_score=0.6,
            bbox_xmin=0,
            bbox_ymin=0,
            bbox_xmax=1,
            bbox_ymax=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    ]

    service = DetectionService(
        detection_repo=det_repo,
        cv_service=mock_cv,
        image_repo=img_repo,
    )

    out = await service.get_detections(image_id)
    assert len(out) == 1
    assert out[0].image_id == image_id


@pytest.mark.asyncio
async def test_get_all_paginated_wraps_response(mock_cv, mock_repos):
    det_repo, img_repo = mock_repos
    items = [
        DummyImage(
            id=uuid4(),
            image_id=uuid4(),
            label="x",
            confidence_score=0.6,
            bbox_xmin=0,
            bbox_ymin=0,
            bbox_xmax=1,
            bbox_ymax=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    ]
    det_repo.get_paginated.return_value = (items, 1)

    service = DetectionService(
        detection_repo=det_repo,
        cv_service=mock_cv,
        image_repo=img_repo,
    )

    resp = await service.get_all_paginated(page=1, page_size=10)
    assert resp.total == 1
    assert len(resp.items) == 1
