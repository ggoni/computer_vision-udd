"""File handling utilities for validating and processing uploaded files."""

import hashlib
import re
from pathlib import Path

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}


def validate_file_extension(filename: str) -> bool:
    """
    Validate that file has an allowed extension.

    Args:
        filename: Name of the file to validate

    Returns:
        True if extension is allowed, False otherwise

    Example:
        >>> validate_file_extension("photo.jpg")
        True
        >>> validate_file_extension("malware.exe")
        False
    """
    if not filename:
        return False

    file_path = Path(filename)
    extension = file_path.suffix.lower()
    return extension in ALLOWED_EXTENSIONS


def validate_file_size(size: int, max_size: int) -> bool:
    """
    Validate that file size is within allowed limits.

    Args:
        size: File size in bytes
        max_size: Maximum allowed size in bytes

    Returns:
        True if size is valid, False otherwise

    Example:
        >>> validate_file_size(1024, 5 * 1024 * 1024)  # 1KB file, 5MB limit
        True
        >>> validate_file_size(10 * 1024 * 1024, 5 * 1024 * 1024)  # 10MB file, 5MB limit
        False
    """
    if size < 0 or max_size < 0:
        return False
    return 0 < size <= max_size


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks.

    - Removes path components (../../)
    - Replaces special characters with underscores
    - Limits length to 255 characters
    - Preserves file extension

    Args:
        filename: Original filename to sanitize

    Returns:
        Sanitized filename safe for storage

    Example:
        >>> sanitize_filename("../../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("my photo!@#$.jpg")
        'my_photo_.jpg'
    """
    if not filename:
        return "unnamed_file"

    # Get just the filename component (remove any path)
    file_path = Path(filename)

    # Split name and extension
    stem = file_path.stem
    suffix = file_path.suffix.lower()

    # Remove any remaining path traversal patterns
    stem = stem.replace("..", "").replace("/", "").replace("\\", "")

    # Replace special characters with underscores
    # Allow only alphanumeric, dash, underscore, and space
    stem = re.sub(r"[^\w\s-]", "_", stem)

    # Replace multiple spaces/underscores with single underscore
    stem = re.sub(r"[\s_]+", "_", stem)

    # Remove leading/trailing underscores
    stem = stem.strip("_")

    # If stem is empty after sanitization, use default
    if not stem:
        stem = "unnamed_file"

    # Combine stem and extension
    sanitized = f"{stem}{suffix}"

    # Limit total length to 255 chars (filesystem limit)
    if len(sanitized) > 255:
        # Truncate stem to fit within limit
        max_stem_length = 255 - len(suffix)
        stem = stem[:max_stem_length]
        sanitized = f"{stem}{suffix}"

    return sanitized


def get_file_hash(file_bytes: bytes) -> str:
    """
    Calculate SHA256 hash of file contents.

    Used for duplicate detection and generating unique filenames.

    Args:
        file_bytes: Raw bytes of the file

    Returns:
        Hexadecimal SHA256 hash string

    Example:
        >>> data = b"test content"
        >>> hash1 = get_file_hash(data)
        >>> hash2 = get_file_hash(data)
        >>> hash1 == hash2
        True
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()
