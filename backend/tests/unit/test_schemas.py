"""Unit tests for Pydantic schemas."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import ValidationError

from src.schemas.image import ImageBase, ImageCreate, ImageUpdate, ImageInDB
from src.schemas.detection import BoundingBox, DetectionBase, DetectionCreate, DetectionInDB
from src.schemas.common import PaginatedResponse


class TestImageSchemas:
    """Tests for Image Pydantic schemas."""

    def test_image_base_valid(self):
        """Test ImageBase with valid data."""
        image = ImageBase(filename="test.jpg", original_url="https://example.com/image.jpg")
        assert image.filename == "test.jpg"
        assert image.original_url == "https://example.com/image.jpg"

    def test_image_base_rejects_path_traversal(self):
        """Test that filename validation prevents path traversal."""
        with pytest.raises(ValidationError) as exc_info:
            ImageBase(filename="../etc/passwd")
        assert "path" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    def test_image_base_rejects_forward_slash(self):
        """Test that filename with forward slash is rejected."""
        with pytest.raises(ValidationError):
            ImageBase(filename="dir/file.jpg")

    def test_image_base_rejects_backslash(self):
        """Test that filename with backslash is rejected."""
        with pytest.raises(ValidationError):
            ImageBase(filename="dir\\file.jpg")

    def test_image_create_inherits_validation(self):
        """Test that ImageCreate inherits filename validation."""
        with pytest.raises(ValidationError):
            ImageCreate(filename="../bad.jpg")

    def test_image_update_allows_optional_fields(self):
        """Test that ImageUpdate has optional fields."""
        update = ImageUpdate(filename="new.jpg")
        assert update.filename == "new.jpg"
        assert update.original_url is None

    def test_image_in_db_from_orm(self):
        """Test ImageInDB can be created from ORM model."""
        data = {
            "id": uuid4(),
            "filename": "test.jpg",
            "storage_path": "/uploads/test.jpg",
            "file_size": 1024,
            "status": "completed",
            "upload_timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        image = ImageInDB(**data)
        assert image.filename == "test.jpg"
        assert image.file_size == 1024


class TestBoundingBox:
    """Tests for BoundingBox schema."""

    def test_valid_bbox(self):
        """Test valid bounding box coordinates."""
        bbox = BoundingBox(xmin=10, ymin=20, xmax=100, ymax=200)
        assert bbox.xmin == 10
        assert bbox.ymax == 200

    def test_bbox_rejects_invalid_x_coords(self):
        """Test that xmax must be greater than xmin."""
        with pytest.raises(ValidationError) as exc_info:
            BoundingBox(xmin=100, ymin=20, xmax=50, ymax=200)
        assert "xmax" in str(exc_info.value).lower()

    def test_bbox_rejects_invalid_y_coords(self):
        """Test that ymax must be greater than ymin."""
        with pytest.raises(ValidationError) as exc_info:
            BoundingBox(xmin=10, ymin=200, xmax=100, ymax=50)
        assert "ymax" in str(exc_info.value).lower()

    def test_bbox_rejects_equal_coords(self):
        """Test that coordinates cannot be equal."""
        with pytest.raises(ValidationError):
            BoundingBox(xmin=50, ymin=50, xmax=50, ymax=100)

    def test_bbox_rejects_negative_coords(self):
        """Test that negative coordinates are rejected."""
        with pytest.raises(ValidationError):
            BoundingBox(xmin=-10, ymin=20, xmax=100, ymax=200)


class TestDetectionSchemas:
    """Tests for Detection Pydantic schemas."""

    def test_detection_base_valid(self):
        """Test DetectionBase with valid data."""
        detection = DetectionBase(
            label="cat",
            confidence_score=0.95,
            bbox_xmin=10,
            bbox_ymin=20,
            bbox_xmax=100,
            bbox_ymax=200,
        )
        assert detection.label == "cat"
        assert detection.confidence_score == 0.95

    def test_detection_validates_bbox_coordinates(self):
        """Test that detection validates bbox coordinates."""
        with pytest.raises(ValidationError):
            DetectionBase(
                label="dog",
                confidence_score=0.8,
                bbox_xmin=100,
                bbox_ymin=20,
                bbox_xmax=50,  # Invalid: less than xmin
                bbox_ymax=200,
            )

    def test_confidence_score_must_be_between_0_and_1(self):
        """Test confidence score range validation."""
        with pytest.raises(ValidationError):
            DetectionBase(
                label="cat",
                confidence_score=1.5,  # Invalid: > 1.0
                bbox_xmin=10,
                bbox_ymin=20,
                bbox_xmax=100,
                bbox_ymax=200,
            )

    def test_confidence_score_accepts_zero(self):
        """Test that confidence score of 0.0 is valid."""
        detection = DetectionBase(
            label="cat",
            confidence_score=0.0,
            bbox_xmin=10,
            bbox_ymin=20,
            bbox_xmax=100,
            bbox_ymax=200,
        )
        assert detection.confidence_score == 0.0

    def test_detection_create_includes_image_id(self):
        """Test DetectionCreate has image_id field."""
        detection = DetectionCreate(
            image_id=uuid4(),
            label="cat",
            confidence_score=0.95,
            bbox_xmin=10,
            bbox_ymin=20,
            bbox_xmax=100,
            bbox_ymax=200,
        )
        assert detection.image_id is not None


class TestPaginatedResponse:
    """Tests for PaginatedResponse schema."""

    def test_paginated_response_calculates_pages(self):
        """Test that pages are calculated correctly."""
        response = PaginatedResponse[int](
            items=[1, 2, 3], total=10, page=1, page_size=3
        )
        assert response.pages == 4  # 10 items / 3 per page = 4 pages
        assert response.has_next is True
        assert response.has_previous is False

    def test_paginated_response_last_page(self):
        """Test last page has no next."""
        response = PaginatedResponse[int](
            items=[10], total=10, page=4, page_size=3
        )
        assert response.has_next is False
        assert response.has_previous is True

    def test_paginated_response_middle_page(self):
        """Test middle page has both next and previous."""
        response = PaginatedResponse[int](
            items=[4, 5, 6], total=10, page=2, page_size=3
        )
        assert response.has_next is True
        assert response.has_previous is True

    def test_paginated_response_empty(self):
        """Test pagination with no items."""
        response = PaginatedResponse[int](
            items=[], total=0, page=1, page_size=10
        )
        assert response.pages == 0
        assert response.has_next is False
        assert response.has_previous is False

    def test_paginated_response_generic_type(self):
        """Test that PaginatedResponse works with different types."""
        # Test with strings
        response = PaginatedResponse[str](
            items=["a", "b"], total=5, page=1, page_size=2
        )
        assert response.items == ["a", "b"]
        assert response.pages == 3
