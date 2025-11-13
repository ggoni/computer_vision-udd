"""Unit tests for image processing utilities."""

from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image

from src.utils.image_processing import (
    MIN_IMAGE_SIZE,
    image_to_bytes,
    preprocess_image,
    resize_image,
)


def create_test_image(
    width: int, height: int, mode: str = "RGB", color: str = "white"
) -> Image.Image:
    """Create an in-memory test image."""
    image = Image.new(mode, (width, height), color=color)
    return image


def image_to_bytes_io(image: Image.Image, format: str = "PNG") -> bytes:
    buffer = BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()


class TestPreprocessImage:
    """Tests for preprocess_image."""

    def test_converts_rgba_to_rgb(self):
        rgba_image = create_test_image(100, 50, mode="RGBA")
        rgba_bytes = image_to_bytes_io(rgba_image, format="PNG")

        processed = preprocess_image(rgba_bytes)

        assert processed.mode == "RGB"
        assert processed.size == (100, 50)

    def test_rejects_small_images(self):
        small_image = create_test_image(MIN_IMAGE_SIZE[0] - 10, MIN_IMAGE_SIZE[1] - 10)
        image_bytes = image_to_bytes_io(small_image)

        with pytest.raises(ValueError):
            preprocess_image(image_bytes)

    def test_rejects_large_images(self):
        large_image = create_test_image(1024, 1024)
        image_bytes = image_to_bytes_io(large_image)

        with pytest.raises(ValueError):
            preprocess_image(image_bytes, max_size=(512, 512))

    def test_rejects_empty_bytes(self):
        with pytest.raises(ValueError):
            preprocess_image(b"")


class TestResizeImage:
    """Tests for resize_image."""

    def test_maintains_aspect_ratio(self):
        image = create_test_image(1000, 2000)
        resized = resize_image(image, max_size=(500, 500))

        assert resized.width == 250
        assert resized.height == 500

    def test_raises_on_invalid_max_size(self):
        image = create_test_image(100, 100)
        with pytest.raises(ValueError):
            resize_image(image, max_size=(0, 100))


class TestImageToBytes:
    """Tests for image_to_bytes."""

    def test_round_trip_image_conversion(self):
        image = create_test_image(64, 64, color="red")
        image_bytes = image_to_bytes(image, format="PNG")

        reloaded = Image.open(BytesIO(image_bytes))
        assert reloaded.size == (64, 64)
        assert reloaded.mode in {"RGB", "RGBA"}

    def test_invalid_format_raises(self):
        image = create_test_image(64, 64)
        with pytest.raises(ValueError):
            image_to_bytes(image, format="INVALID_FORMAT")
