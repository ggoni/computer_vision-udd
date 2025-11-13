"""Common Pydantic schemas."""

from math import ceil
from typing import TypeVar

from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class PaginatedResponse[T](BaseModel):
    """Generic paginated response schema."""

    items: list[T] = Field(..., description="List of items for current page")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, description="Number of items per page")

    @computed_field  # type: ignore[misc]
    @property
    def pages(self) -> int:
        """Calculate total number of pages."""
        if self.page_size <= 0:
            return 0
        return ceil(self.total / self.page_size)

    @computed_field  # type: ignore[misc]
    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.pages

    @computed_field  # type: ignore[misc]
    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1

    model_config = {"from_attributes": True}
