"""Unit tests for FileStorage service."""

from pathlib import Path

from src.utils.file_storage import FileStorage


class TestFileStorage:
    """Tests for FileStorage class."""

    def test_save_file_creates_directory_structure(self, tmp_path):
        """Test that save_file creates timestamped directories."""
        storage = FileStorage(upload_dir=tmp_path)
        file_bytes = b"test image data"

        path = storage.save_file(file_bytes, "test.jpg")

        assert storage.file_exists(path)
        saved_file = storage.get_file_path(path)
        assert saved_file.read_bytes() == file_bytes

    def test_save_file_generates_unique_filename(self, tmp_path):
        """Test that save_file uses hash prefix for uniqueness."""
        storage = FileStorage(upload_dir=tmp_path)
        file_bytes = b"unique content"

        path = storage.save_file(file_bytes, "photo.jpg")
        filename = Path(path).name

        # Should have format: hash_filename.ext
        assert "_" in filename
        assert filename.endswith(".jpg")
        # Hash prefix should be 8 chars
        hash_prefix = filename.split("_")[0]
        assert len(hash_prefix) == 8

    def test_save_file_sanitizes_filename(self, tmp_path):
        """Test that dangerous filenames are sanitized."""
        storage = FileStorage(upload_dir=tmp_path)
        file_bytes = b"data"

        path = storage.save_file(file_bytes, "../../etc/passwd")
        filename = Path(path).name

        # Should not contain path traversal
        assert ".." not in filename
        assert "/" not in filename

    def test_delete_file_removes_file(self, tmp_path):
        """Test that delete_file removes the file."""
        storage = FileStorage(upload_dir=tmp_path)
        path = storage.save_file(b"data", "test.jpg")

        assert storage.file_exists(path)
        result = storage.delete_file(path)

        assert result is True
        assert storage.file_exists(path) is False

    def test_delete_nonexistent_file_returns_false(self, tmp_path):
        """Test deleting non-existent file returns False."""
        storage = FileStorage(upload_dir=tmp_path)

        result = storage.delete_file("nonexistent/file.jpg")

        assert result is False

    def test_file_exists_returns_false_for_missing(self, tmp_path):
        """Test file_exists returns False for missing files."""
        storage = FileStorage(upload_dir=tmp_path)

        assert storage.file_exists("missing/file.jpg") is False

    def test_get_file_path_returns_absolute_path(self, tmp_path):
        """Test get_file_path returns absolute Path."""
        storage = FileStorage(upload_dir=tmp_path)

        result = storage.get_file_path("2025/11/12/test.jpg")

        assert isinstance(result, Path)
        assert result.is_absolute()
        assert "2025/11/12/test.jpg" in str(result)

    def test_get_file_size_returns_correct_size(self, tmp_path):
        """Test get_file_size returns correct byte count."""
        storage = FileStorage(upload_dir=tmp_path)
        file_bytes = b"test data with known size"
        path = storage.save_file(file_bytes, "test.jpg")

        size = storage.get_file_size(path)

        assert size == len(file_bytes)

    def test_get_file_size_returns_none_for_missing(self, tmp_path):
        """Test get_file_size returns None for missing files."""
        storage = FileStorage(upload_dir=tmp_path)

        size = storage.get_file_size("missing/file.jpg")

        assert size is None

    def test_multiple_files_same_name_different_content(self, tmp_path):
        """Test that same filename with different content creates different files."""
        storage = FileStorage(upload_dir=tmp_path)

        path1 = storage.save_file(b"content1", "photo.jpg")
        path2 = storage.save_file(b"content2", "photo.jpg")

        # Paths should be different due to different hashes
        assert path1 != path2
        assert storage.file_exists(path1)
        assert storage.file_exists(path2)
