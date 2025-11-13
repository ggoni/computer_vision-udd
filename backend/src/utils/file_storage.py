"""File storage service for saving and retrieving uploaded files."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..core.config import get_settings
from .file_utils import get_file_hash, sanitize_filename

logger = logging.getLogger(__name__)


class FileStorage:
    """
    Service for managing file storage operations.

    Handles saving, retrieving, and deleting files with organized directory structure.
    Files are stored in timestamped subdirectories (YYYY/MM/DD) for better organization.
    """

    def __init__(self, upload_dir: Path | None = None):
        """
        Initialize FileStorage service.

        Args:
            upload_dir: Base directory for file uploads. If None, uses settings.
        """
        if upload_dir is None:
            settings = get_settings()
            upload_dir = settings.upload_path

        self.upload_dir = Path(upload_dir)
        self._ensure_upload_dir()

    def _ensure_upload_dir(self) -> None:
        """Create upload directory if it doesn't exist."""
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Upload directory ready: {self.upload_dir}")
        except Exception as e:
            logger.error(f"Failed to create upload directory: {e}")
            raise

    def _get_timestamped_dir(self) -> Path:
        """
        Get timestamped subdirectory for current date (YYYY/MM/DD).

        Returns:
            Path to timestamped directory
        """
        # Use timezone-aware UTC datetime to avoid deprecation warnings and ensure consistency
        now = datetime.now(UTC)
        date_path = Path(str(now.year)) / f"{now.month:02d}" / f"{now.day:02d}"
        full_path = self.upload_dir / date_path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path

    def save_file(self, file_bytes: bytes, filename: str) -> str:
        """
        Save file to storage with unique filename.

        Generates unique filename using file hash and original name.
        Stores in timestamped subdirectory for organization.

        Args:
            file_bytes: Raw bytes of the file
            filename: Original filename

        Returns:
            Relative storage path from upload_dir (e.g., "2025/11/12/abc123_photo.jpg")

        Raises:
            IOError: If file cannot be saved

        Example:
            >>> storage = FileStorage()
            >>> path = storage.save_file(b"image data", "photo.jpg")
            >>> print(path)
            "2025/11/12/a3f2b1c_photo.jpg"
        """
        try:
            # Sanitize original filename
            clean_filename = sanitize_filename(filename)

            # Generate file hash for uniqueness
            file_hash = get_file_hash(file_bytes)

            # Create unique filename: hash_prefix + original_name; ensure uniqueness if collision
            hash_prefix = file_hash[:8]
            file_path = Path(clean_filename)
            base_name = f"{hash_prefix}_{file_path.stem}{file_path.suffix}"

            # Get timestamped directory
            target_dir = self._get_timestamped_dir()
            target_path = target_dir / base_name
            # Handle collision by appending short random suffix until unique
            while target_path.exists():  # pragma: no cover - rare collision path
                suffix = uuid4().hex[:4]
                target_path = (
                    target_dir
                    / f"{hash_prefix}_{file_path.stem}_{suffix}{file_path.suffix}"
                )

            # Save file
            target_path.write_bytes(file_bytes)

            # Return relative path from upload_dir
            relative_path = target_path.relative_to(self.upload_dir)
            storage_path = str(relative_path)

            logger.info(f"File saved: {storage_path} ({len(file_bytes)} bytes)")
            return storage_path

        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            raise OSError(f"Could not save file: {e}") from e

    def get_file_path(self, storage_path: str) -> Path:
        """
        Get absolute filesystem path for a stored file.

        Args:
            storage_path: Relative storage path from save_file()

        Returns:
            Absolute Path object to the file

        Example:
            >>> storage = FileStorage()
            >>> path = storage.get_file_path("2025/11/12/abc123_photo.jpg")
            >>> print(path)
            PosixPath('/app/storage/uploads/2025/11/12/abc123_photo.jpg')
        """
        return self.upload_dir / storage_path

    def file_exists(self, storage_path: str) -> bool:
        """
        Check if file exists in storage.

        Args:
            storage_path: Relative storage path

        Returns:
            True if file exists, False otherwise

        Example:
            >>> storage = FileStorage()
            >>> storage.file_exists("2025/11/12/abc123_photo.jpg")
            True
        """
        try:
            file_path = self.get_file_path(storage_path)
            return file_path.exists() and file_path.is_file()
        except Exception as e:
            logger.warning(f"Error checking file existence: {e}")
            return False

    def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            storage_path: Relative storage path

        Returns:
            True if file was deleted, False if file didn't exist or error occurred

        Example:
            >>> storage = FileStorage()
            >>> storage.delete_file("2025/11/12/abc123_photo.jpg")
            True
        """
        try:
            file_path = self.get_file_path(storage_path)

            if not file_path.exists():
                logger.warning(f"Cannot delete non-existent file: {storage_path}")
                return False

            file_path.unlink()
            logger.info(f"File deleted: {storage_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file {storage_path}: {e}")
            return False

    def get_file_size(self, storage_path: str) -> int | None:
        """
        Get size of stored file in bytes.

        Args:
            storage_path: Relative storage path

        Returns:
            File size in bytes, or None if file doesn't exist
        """
        try:
            file_path = self.get_file_path(storage_path)
            if file_path.exists():
                return file_path.stat().st_size
            return None
        except Exception as e:
            logger.warning(f"Error getting file size: {e}")
            return None
