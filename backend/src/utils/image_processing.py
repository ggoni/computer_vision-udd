"""Image preprocessing utilities for computer vision inference."""

from __future__ import annotations

from io import BytesIO
from typing import Tuple

from PIL import Image, ImageOps, UnidentifiedImageError

# Supported image formats for uploads
SUPPORTED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}

# Minimum and maximum allowed dimensions (width, height)
MIN_IMAGE_SIZE: Tuple[int, int] = (32, 32)
MAX_IMAGE_SIZE: Tuple[int, int] = (8192, 8192)


def preprocess_image(
    image_bytes: bytes,
    *,
    min_size: Tuple[int, int] | None = None,
    max_size: Tuple[int, int] | None = None,
) -> Image.Image:
    """Load and validate an image from raw bytes, returning an RGB PIL image.

    Args:
        image_bytes: Raw bytes representing the image file.
        min_size: Optional override for minimum (width, height).
        max_size: Optional override for maximum (width, height).

    Returns:
        A PIL ``Image`` instance in RGB color space.

    Raises:
        ValueError: If the image is invalid, unsupported, or outside size bounds.
    """

    min_w, min_h = min_size or MIN_IMAGE_SIZE
    max_w, max_h = max_size or MAX_IMAGE_SIZE

    if not image_bytes:
        raise ValueError("Image data is empty")

    try:
        with Image.open(BytesIO(image_bytes)) as img:
            img.load()
            image_format = (img.format or "").upper()
            image = img.convert("RGBA") if img.mode in {"P", "LA"} else img.copy()
    except (UnidentifiedImageError, OSError) as exc:  # pragma: no cover - PIL exceptions
        raise ValueError("Provided file is not a valid image") from exc

    if image_format and image_format not in SUPPORTED_IMAGE_FORMATS:
        raise ValueError(f"Unsupported image format: {image_format}")

    width, height = image.size
    if width < min_w or height < min_h:
        raise ValueError(
            f"Image dimensions {width}x{height} smaller than minimum {min_w}x{min_h}"
        )
    if width > max_w or height > max_h:
        raise ValueError(
            f"Image dimensions {width}x{height} exceed maximum {max_w}x{max_h}"
        )

    # Ensure image is RGB for downstream models
    if image.mode != "RGB":
        image = image.convert("RGB")

    return image


def resize_image(
    image: Image.Image,
    max_size: Tuple[int, int],
    *,
    resample: Image.Resampling = Image.Resampling.LANCZOS,
) -> Image.Image:
    """Resize an image to fit within ``max_size`` while preserving aspect ratio."""

    if max_size[0] <= 0 or max_size[1] <= 0:
        raise ValueError("max_size dimensions must be positive")

    # ImageOps.contain returns a new image resized to fit within the box
    resized = ImageOps.contain(image, max_size, method=resample)
    return resized


def image_to_bytes(image: Image.Image, format: str = "JPEG", **save_kwargs) -> bytes:
    """Serialize a PIL image back into bytes."""

    buffer = BytesIO()
    try:
        image.save(buffer, format=format, **save_kwargs)
    except (OSError, KeyError) as exc:  # pragma: no cover - depends on Pillow internals
        raise ValueError(f"Failed to encode image as {format}") from exc
    return buffer.getvalue()
