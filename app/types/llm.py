"""LLM-related type definitions."""

from typing import TypedDict, Optional


class LLMConfig(TypedDict, total=False):
    """Configuration for LLM."""
    provider: str
    model: str
    api_key: str
    base_url: Optional[str]
    temperature: float
    max_tokens: int
    top_p: Optional[float]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]
    enable_guardrail: bool


class LLMValidationResult(TypedDict, total=False):
    """Result of LLM input/output validation."""
    valid: bool
    is_safe: bool
    blocked: bool
    reason: Optional[str]
    details: Optional[dict[str, float]]
