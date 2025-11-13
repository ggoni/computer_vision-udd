"""Performance monitoring middleware for FastAPI applications.

This module provides performance tracking, request logging, and metrics
collection to help monitor application health and identify bottlenecks.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.logging import get_logger

logger = get_logger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking request performance and logging.
    
    Measures request duration, logs slow requests, and provides
    structured logging for debugging and monitoring purposes.
    """

    def __init__(self, app, slow_request_threshold: float = 1.0):
        """Initialize performance monitoring middleware.
        
        Args:
            app: FastAPI application instance
            slow_request_threshold: Time in seconds to consider a request slow
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with performance monitoring.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain
            
        Returns:
            HTTP response with added performance headers
        """
        start_time = time.time()
        
        # Extract request info for logging
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Add correlation ID for request tracking
        correlation_id = request.headers.get("x-correlation-id", f"req_{int(start_time * 1000000)}")
        
        logger.info(
            "Request started",
            extra={
                "correlation_id": correlation_id,
                "method": method,
                "url": url,
                "client_ip": client_ip,
                "user_agent": user_agent,
            }
        )

        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate performance metrics
            duration = time.time() - start_time
            status_code = response.status_code
            
            # Log performance metrics
            log_level = "warning" if duration > self.slow_request_threshold else "info"
            log_message = "Slow request completed" if duration > self.slow_request_threshold else "Request completed"
            
            getattr(logger, log_level)(
                log_message,
                extra={
                    "correlation_id": correlation_id,
                    "method": method,
                    "url": url,
                    "status_code": status_code,
                    "duration": round(duration, 3),
                    "client_ip": client_ip,
                }
            )
            
            # Add performance headers to response
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Log error with context
            duration = time.time() - start_time
            
            logger.error(
                "Request failed with exception",
                extra={
                    "correlation_id": correlation_id,
                    "method": method,
                    "url": url,
                    "duration": round(duration, 3),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "client_ip": client_ip,
                }
            )
            
            # Re-raise the exception to be handled by FastAPI
            raise


class DatabaseQueryMonitor:
    """Context manager for monitoring database query performance."""
    
    def __init__(self, operation_name: str, correlation_id: str = None):
        """Initialize database query monitor.
        
        Args:
            operation_name: Name of the database operation
            correlation_id: Request correlation ID for tracking
        """
        self.operation_name = operation_name
        self.correlation_id = correlation_id
        self.start_time = None
        
    async def __aenter__(self):
        """Start monitoring database operation."""
        self.start_time = time.time()
        logger.debug(
            f"Database operation started: {self.operation_name}",
            extra={
                "correlation_id": self.correlation_id,
                "operation": self.operation_name,
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End monitoring and log results."""
        duration = time.time() - self.start_time
        
        if exc_type is None:
            # Successful operation
            log_level = "warning" if duration > 0.5 else "debug"
            log_message = f"Database operation completed: {self.operation_name}"
            
            getattr(logger, log_level)(
                log_message,
                extra={
                    "correlation_id": self.correlation_id,
                    "operation": self.operation_name,
                    "duration": round(duration, 3),
                    "success": True,
                }
            )
        else:
            # Failed operation
            logger.error(
                f"Database operation failed: {self.operation_name}",
                extra={
                    "correlation_id": self.correlation_id,
                    "operation": self.operation_name,
                    "duration": round(duration, 3),
                    "success": False,
                    "error": str(exc_val),
                    "error_type": exc_type.__name__,
                }
            )