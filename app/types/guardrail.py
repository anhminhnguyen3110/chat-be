"""Guardrail-related type definitions."""

from typing import TypedDict, Optional


class GuardrailValidationResult(TypedDict, total=False):
    """Result of guardrail validation."""
    is_safe: bool
    blocked: bool
    reason: Optional[str]
    categories: Optional[list[str]]
    confidence: Optional[float]
    details: Optional[dict[str, float]]


class GuardrailConfig(TypedDict, total=False):
    """Configuration for guardrail."""
    enabled: bool
    threshold: float
    categories: list[str]
    provider: str
