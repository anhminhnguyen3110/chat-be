"""MCP (Model Context Protocol) related type definitions."""

from typing import TypedDict, Optional, Any


class MCPConfig(TypedDict, total=False):
    """Configuration for MCP client."""
    uri: str
    user: str
    password: str
    database: str
    timeout: Optional[int]


class MCPExecuteParams(TypedDict, total=False):
    """Parameters for MCP execute command."""
    query: str
    params: Optional[dict[str, Any]]


class CypherExecutionResult(TypedDict, total=False):
    """Result of Cypher query execution."""
    records: list[dict[str, Any]]
    count: int
    error: Optional[str]


class Neo4jSchemaResult(TypedDict, total=False):
    """Neo4j schema information."""
    nodes: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    properties: dict[str, list[str]]
    indexes: list[dict[str, Any]]
    constraints: list[dict[str, Any]]


class Neo4jValidationResult(TypedDict, total=False):
    """Result of Neo4j query validation."""
    valid: bool
    errors: list[str]
    warnings: list[str]
    suggestion: Optional[str]


class Neo4jExplainResult(TypedDict, total=False):
    """Result of EXPLAIN query."""
    plan: dict[str, Any]
    estimated_rows: Optional[int]
    db_hits: Optional[int]
