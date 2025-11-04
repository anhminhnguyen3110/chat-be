"""Tool-related type definitions."""

from typing import TypedDict, Any


class ToolParams(TypedDict, total=False):
    """Parameters for tool execution."""
    prompt: str
    query: str
    context: str
    options: dict[str, Any]


class ToolResult(TypedDict, total=False):
    """Result of tool execution."""
    result: str
    success: bool
    error: str
    metadata: dict[str, Any]


class ThinkToolResult(TypedDict, total=False):
    """Result from think tool."""
    thinking: str
    reasoning: str


class PlanToolResult(TypedDict, total=False):
    """Result from plan tool."""
    plan: dict[str, Any]
    steps: list[str]
    strategy: str
