"""API middleware for error handling and request processing."""

import traceback
from typing import Any

from fastapi import HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import get_settings
from ..core.logging import get_logger, set_correlation_id

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling and logging."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and handle errors.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response: HTTP response
        """
        # Generate correlation ID
        correlation_id = request.headers.get(
            "X-Correlation-ID", self._generate_correlation_id()
        )
        set_correlation_id(correlation_id)

        # Add correlation ID to response headers
        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response

        except Exception as exc:
            return await self._handle_exception(request, exc, correlation_id)

    async def _handle_exception(
        self, request: Request, exc: Exception, correlation_id: str
    ) -> JSONResponse:
        """Handle and format exceptions.

        Args:
            request: HTTP request
            exc: Exception that occurred
            correlation_id: Request correlation ID

        Returns:
            JSONResponse: Formatted error response
        """
        settings = get_settings()

        # Build error context
        error_context = {
            "method": request.method,
            "url": str(request.url),
            "correlation_id": correlation_id,
        }

        # Handle different exception types
        if isinstance(exc, HTTPException):
            logger.warning(
                f"HTTP exception: {exc.detail}",
                extra={**error_context, "status_code": exc.status_code},
            )
            return self._create_error_response(
                status_code=exc.status_code,
                error_code="HTTP_ERROR",
                message=str(exc.detail),
                correlation_id=correlation_id,
                include_detail=settings.DEBUG,
            )

        elif isinstance(exc, RequestValidationError):
            logger.warning(
                "Request validation failed",
                extra={**error_context, "validation_errors": exc.errors()},
            )
            return self._create_error_response(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="VALIDATION_ERROR",
                message="Request validation failed",
                detail=exc.errors() if settings.DEBUG else None,
                correlation_id=correlation_id,
            )

        else:
            # Unexpected server error
            logger.error(
                f"Unexpected error: {str(exc)}",
                extra={
                    **error_context,
                    "exception_type": type(exc).__name__,
                    "traceback": traceback.format_exc() if settings.DEBUG else None,
                },
            )
            return self._create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                detail=str(exc) if settings.DEBUG else None,
                correlation_id=correlation_id,
            )

    def _create_error_response(
        self,
        status_code: int,
        error_code: str,
        message: str,
        correlation_id: str,
        detail: Any = None,
        include_detail: bool = True,
    ) -> JSONResponse:
        """Create standardized error response.

        Args:
            status_code: HTTP status code
            error_code: Application error code
            message: Human-readable error message
            correlation_id: Request correlation ID
            detail: Additional error details
            include_detail: Whether to include detail in response

        Returns:
            JSONResponse: Formatted error response
        """
        response_body = {
            "error": error_code,
            "message": message,
            "correlation_id": correlation_id,
        }

        if detail is not None and include_detail:
            response_body["detail"] = detail

        return JSONResponse(
            status_code=status_code,
            content=response_body,
            headers={"X-Correlation-ID": correlation_id},
        )

    def _generate_correlation_id(self) -> str:
        """Generate a new correlation ID.

        Returns:
            str: New correlation ID
        """
        import uuid

        return str(uuid.uuid4())[:8]
