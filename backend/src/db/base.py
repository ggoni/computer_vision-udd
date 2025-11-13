"""SQLAlchemy database base configuration and mixins.

This module provides the declarative base class and common mixins
for all database models in the application.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


class UUIDMixin:
    """Mixin for models that need a UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Primary key UUID",
    )


class TimestampMixin:
    """Mixin for models that need created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Record last update timestamp",
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base model class with UUID and timestamp mixins.

    This class combines the declarative base with common mixins
    that most models in the application will need.
    """

    __abstract__ = True

    def __repr__(self) -> str:
        """Return string representation of the model."""
        attrs = []
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                attrs.append(f"{key}={value!r}")

        return f"<{self.__class__.__name__}({', '.join(attrs)})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert datetime to ISO string for JSON serialization
            if isinstance(value, datetime):
                value = value.isoformat()
            # Convert UUID to string
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value

        return result
