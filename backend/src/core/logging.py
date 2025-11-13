"""Structured logging configuration with JSON formatter.

This module provides centralized logging setup with JSON formatting for production
and human-readable formatting for development. Includes correlation ID support.
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime

from .config import get_settings

# Context variable for request correlation ID
correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON formatted log entry
        """
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation ID if available
        if corr_id := correlation_id.get():
            log_entry["correlation_id"] = corr_id

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from the log record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "getMessage",
                "exc_info", "exc_text", "stack_info"
            } and key not in log_entry:
                # Safely add extra fields, avoid overwriting existing keys
                extra_fields[key] = value

        if extra_fields:
            log_entry["extra"] = extra_fields

        return json.dumps(log_entry, default=str, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development console output."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for development.

        Args:
            record: Log record to format

        Returns:
            Colored formatted log entry
        """
        # Get color for level
        color = self.COLORS.get(record.levelname, "")
        reset = self.COLORS["RESET"]

        # Format timestamp
        timestamp = datetime.utcnow().strftime("%H:%M:%S")

        # Build log line
        log_parts = [
            f"{color}{record.levelname:<8}{reset}",
            f"[{timestamp}]",
            f"{record.name}:",
            record.getMessage(),
        ]

        # Add correlation ID if available
        if corr_id := correlation_id.get():
            log_parts.insert(-1, f"[{corr_id[:8]}]")

        return " ".join(log_parts)


def setup_logging() -> None:
    """Configure application logging based on settings.

    Sets up structured JSON logging for production and colored
    console logging for development.
    """
    settings = get_settings()

    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Choose formatter based on environment
    formatter = JSONFormatter() if settings.is_production else ColoredFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Log the setup
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "environment": settings.APP_ENV,
            "log_level": settings.LOG_LEVEL,
            "formatter": "JSON" if settings.is_production else "Colored",
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(corr_id: str) -> None:
    """Set correlation ID for current context.

    Args:
        corr_id: Correlation ID to set
    """
    correlation_id.set(corr_id)


def get_correlation_id() -> str | None:
    """Get current correlation ID.

    Returns:
        Current correlation ID or None
    """
    return correlation_id.get()
