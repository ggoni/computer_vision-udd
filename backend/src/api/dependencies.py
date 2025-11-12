"""FastAPI dependency injection functions.

This module provides reusable dependencies for request handling,
validation, and resource access.
"""

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, Request, UploadFile, status

from ..core.config import Settings, get_settings
from ..core.logging import get_correlation_id, get_logger, set_correlation_id
from ..db.session import AsyncSession, get_db as _get_db

logger = get_logger(__name__)


def get_db() -> AsyncSession:
    """Database session dependency.
    
    Returns:
        AsyncSession: Database session for the request
    """
    return Depends(_get_db)


def get_current_settings() -> Settings:
    """Settings dependency.
    
    Returns:
        Settings: Application settings
    """
    return Depends(get_settings)


def get_correlation_id_from_request(request: Request) -> str:
    """Extract or generate correlation ID for request tracking.
    
    Args:
        request: HTTP request
        
    Returns:
        str: Correlation ID for the request
    """
    # Try to get from header first
    correlation_id = request.headers.get("X-Correlation-ID")
    
    if not correlation_id:
        # Generate new correlation ID
        correlation_id = str(uuid.uuid4())[:8]
        logger.debug("Generated new correlation ID", extra={"correlation_id": correlation_id})
    
    # Set in context for logging
    set_correlation_id(correlation_id)
    
    return correlation_id


async def verify_upload_size(
    file: UploadFile,
    settings: Settings = Depends(get_settings)
) -> UploadFile:
    """Validate uploaded file size.
    
    Args:
        file: Uploaded file
        settings: Application settings
        
    Returns:
        UploadFile: Validated file
        
    Raises:
        HTTPException: If file is too large
    """
    # Read file to check size
    content = await file.read()
    file_size = len(content)
    
    # Reset file pointer
    await file.seek(0)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        logger.warning(
            "File upload rejected - too large",
            extra={
                "filename": file.filename,
                "file_size": file_size,
                "max_size": settings.MAX_UPLOAD_SIZE
            }
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "FILE_TOO_LARGE",
                "message": f"File size {file_size} exceeds maximum {settings.MAX_UPLOAD_SIZE} bytes",
                "max_size_mb": settings.MAX_UPLOAD_SIZE // (1024 * 1024)
            }
        )
    
    logger.info(
        "File upload size validated",
        extra={
            "filename": file.filename,
            "file_size": file_size
        }
    )
    
    return file


def validate_image_file(file: UploadFile) -> UploadFile:
    """Validate that uploaded file is an image.
    
    Args:
        file: Uploaded file
        
    Returns:
        UploadFile: Validated image file
        
    Raises:
        HTTPException: If file is not a valid image type
    """
    # Check content type
    allowed_types = {
        "image/jpeg", "image/jpg", "image/png", 
        "image/gif", "image/bmp", "image/webp"
    }
    
    if file.content_type not in allowed_types:
        logger.warning(
            "File upload rejected - invalid type",
            extra={
                "filename": file.filename,
                "content_type": file.content_type,
                "allowed_types": list(allowed_types)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_FILE_TYPE",
                "message": f"File type '{file.content_type}' not supported",
                "allowed_types": list(allowed_types)
            }
        )
    
    # Check file extension
    if file.filename:
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
        file_extension = "." + file.filename.split(".")[-1].lower()
        
        if file_extension not in allowed_extensions:
            logger.warning(
                "File upload rejected - invalid extension",
                extra={
                    "filename": file.filename,
                    "extension": file_extension,
                    "allowed_extensions": list(allowed_extensions)
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_FILE_EXTENSION",
                    "message": f"File extension '{file_extension}' not supported",
                    "allowed_extensions": list(allowed_extensions)
                }
            )
    
    logger.info(
        "Image file validated",
        extra={
            "filename": file.filename,
            "content_type": file.content_type
        }
    )
    
    return file


# Composite dependency for complete file validation
async def validate_uploaded_image(
    file: UploadFile,
    settings: Settings = Depends(get_settings)
) -> UploadFile:
    """Complete validation for uploaded image files.
    
    Combines size and type validation.
    
    Args:
        file: Uploaded file
        settings: Application settings
        
    Returns:
        UploadFile: Fully validated image file
    """
    # Validate image type first
    validated_file = validate_image_file(file)
    
    # Then validate size
    validated_file = await verify_upload_size(validated_file, settings)
    
    return validated_file