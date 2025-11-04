"""Common type definitions used across the application."""

from typing import TypedDict, Any, Optional


class ErrorDetails(TypedDict, total=False):
    """Error details structure."""
    code: str
    message: str
    field: Optional[str]
    details: Optional[str]


class MetadataDict(TypedDict, total=False):
    """Generic metadata dictionary with common fields."""
    session_id: Optional[str | int]
    user_id: Optional[str]
    timestamp: Optional[str]
    source: Optional[str]
    tags: Optional[list[str]]
    extra: Optional[dict[str, Any]]
