"""Unit tests for file utilities."""

import pytest
from src.utils.file_utils import (
    ALLOWED_EXTENSIONS,
    validate_file_extension,
    validate_file_size,
    sanitize_filename,
    get_file_hash,
)


class TestValidateFileExtension:
    """Tests for validate_file_extension function."""

    def test_allows_jpg(self):
        assert validate_file_extension("image.jpg") is True

    def test_allows_jpeg(self):
        assert validate_file_extension("photo.jpeg") is True

    def test_allows_png(self):
        assert validate_file_extension("screenshot.png") is True

    def test_allows_webp(self):
        assert validate_file_extension("modern.webp") is True

    def test_rejects_exe(self):
        assert validate_file_extension("malware.exe") is False

    def test_rejects_sh(self):
        assert validate_file_extension("script.sh") is False

    def test_case_insensitive(self):
        assert validate_file_extension("IMAGE.JPG") is True
        assert validate_file_extension("Photo.PNG") is True

    def test_empty_filename(self):
        assert validate_file_extension("") is False


class TestValidateFileSize:
    """Tests for validate_file_size function."""

    def test_valid_size_within_limit(self):
        assert validate_file_size(1024, 5 * 1024 * 1024) is True  # 1KB < 5MB

    def test_exact_max_size(self):
        assert validate_file_size(5 * 1024 * 1024, 5 * 1024 * 1024) is True

    def test_exceeds_limit(self):
        assert validate_file_size(10 * 1024 * 1024, 5 * 1024 * 1024) is False

    def test_zero_size(self):
        assert validate_file_size(0, 5 * 1024 * 1024) is False

    def test_negative_size(self):
        assert validate_file_size(-100, 5 * 1024 * 1024) is False

    def test_negative_max_size(self):
        assert validate_file_size(1024, -100) is False


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_removes_path_traversal(self):
        result = sanitize_filename("../../etc/passwd")
        assert "/" not in result
        assert ".." not in result
        # Path components are removed, leaving just the final filename
        assert result == "passwd"

    def test_replaces_special_characters(self):
        result = sanitize_filename("my photo!@#$.jpg")
        # Special chars replaced with underscore, then collapsed
        assert result == "my_photo.jpg"

    def test_preserves_extension(self):
        result = sanitize_filename("test.jpg")
        assert result.endswith(".jpg")

    def test_handles_spaces(self):
        result = sanitize_filename("my  photo   file.png")
        assert result == "my_photo_file.png"

    def test_removes_backslashes(self):
        result = sanitize_filename("C:\\Users\\test.jpg")
        assert "\\" not in result

    def test_limits_length(self):
        long_name = "a" * 300 + ".jpg"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_empty_filename_gets_default(self):
        result = sanitize_filename("")
        assert result == "unnamed_file"

    def test_preserves_normal_filename(self):
        result = sanitize_filename("normal_photo.jpg")
        assert result == "normal_photo.jpg"


class TestGetFileHash:
    """Tests for get_file_hash function."""

    def test_hash_is_consistent(self):
        data = b"test content"
        hash1 = get_file_hash(data)
        hash2 = get_file_hash(data)
        assert hash1 == hash2

    def test_different_content_different_hash(self):
        hash1 = get_file_hash(b"content1")
        hash2 = get_file_hash(b"content2")
        assert hash1 != hash2

    def test_hash_is_hex_string(self):
        data = b"test"
        result = get_file_hash(data)
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 produces 64 hex chars
        # Check all characters are valid hex
        assert all(c in "0123456789abcdef" for c in result)

    def test_empty_data(self):
        result = get_file_hash(b"")
        assert isinstance(result, str)
        assert len(result) == 64


class TestAllowedExtensions:
    """Tests for ALLOWED_EXTENSIONS constant."""

    def test_contains_expected_extensions(self):
        assert ".jpg" in ALLOWED_EXTENSIONS
        assert ".jpeg" in ALLOWED_EXTENSIONS
        assert ".png" in ALLOWED_EXTENSIONS
        assert ".webp" in ALLOWED_EXTENSIONS

    def test_is_set(self):
        assert isinstance(ALLOWED_EXTENSIONS, set)
