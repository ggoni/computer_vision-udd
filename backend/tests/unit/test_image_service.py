import pytest
import pytest_asyncio
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock, ANY, AsyncMock

from src.services.image_service import ImageService
from src.schemas.image import ImageInDB


class DummyImage:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest_asyncio.fixture
async def mock_repo():
    repo = Mock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.update_status = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest_asyncio.fixture
async def mock_storage():
    storage = Mock()
    storage.save_file.return_value = "2025/11/12/abcd_test.jpg"
    storage.delete_file.return_value = True
    return storage


@pytest.mark.asyncio
async def test_save_uploaded_image_validates_extension(mock_repo, mock_storage):
    service = ImageService(mock_repo, mock_storage)

    with pytest.raises(ValueError):
        await service.save_uploaded_image(file_bytes=b"data", filename="malware.exe")


@pytest.mark.asyncio
async def test_save_uploaded_image_persists_storage_and_repo(mock_repo, mock_storage):
    service = ImageService(mock_repo, mock_storage)

    # Arrange repo.create to return a dummy ORM-like object
    dummy = DummyImage(
        id=uuid4(),
        filename="photo.jpg",
        original_url=None,
        storage_path="2025/11/12/abcd_photo.jpg",
        file_size=4,
        status="pending",
        upload_timestamp=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_repo.create.return_value = dummy

    result = await service.save_uploaded_image(file_bytes=b"data", filename="photo.jpg")

    # Storage called
    mock_storage.save_file.assert_called_once()
    # Repo called with expected keys
    args, _ = mock_repo.create.call_args
    assert "filename" in args[0]
    assert "storage_path" in args[0]
    assert "file_size" in args[0]

    assert isinstance(result, ImageInDB)
    assert result.filename == "photo.jpg"


@pytest.mark.asyncio
async def test_get_image_passthrough(mock_repo, mock_storage):
    service = ImageService(mock_repo, mock_storage)
    image_id = uuid4()

    mock_repo.get_by_id.return_value = DummyImage(
        id=image_id,
        filename="x.jpg",
        original_url=None,
        storage_path="p",
        file_size=1,
        status="pending",
        upload_timestamp=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    result = await service.get_image(image_id)
    assert result is not None
    assert result.id == image_id


@pytest.mark.asyncio
async def test_delete_image_removes_storage_then_repo(mock_repo, mock_storage):
    service = ImageService(mock_repo, mock_storage)
    image_id = uuid4()

    # Found image
    mock_repo.get_by_id.return_value = DummyImage(
        id=image_id,
        filename="x.jpg",
        original_url=None,
        storage_path="2025/11/12/abcd_x.jpg",
        file_size=1,
        status="pending",
        upload_timestamp=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_repo.delete.return_value = True

    ok = await service.delete_image(image_id)
    assert ok is True
    mock_storage.delete_file.assert_called_once()
    mock_repo.delete.assert_called_once_with(image_id)
