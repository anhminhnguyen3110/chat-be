"""Agent-related type definitions."""

from typing import TypedDict, Optional, Any, List
from app.types.common import MetadataDict


class AgentConfig(TypedDict, total=False):
    """Configuration for agent initialization."""
    llm_provider: str
    model: str
    temperature: float
    max_tokens: int
    enable_langfuse: bool
    enable_guardrail: bool
    max_history: int
    max_context_tokens: int
    neo4j_config: Optional["Neo4jConfig"]
    vectorstore_config: Optional["VectorStoreConfig"]


class LangGraphConfig(TypedDict, total=False):
    """LangGraph execution configuration."""
    configurable: dict[str, any]
    callbacks: Optional[List[any]]
    metadata: Optional[MetadataDict]
    tags: Optional[List[str]]
    recursion_limit: Optional[int]


class Neo4jConfig(TypedDict, total=False):
    """Neo4j specific configuration."""
    uri: str
    user: str
    password: str
    database: str


class VectorStoreConfig(TypedDict, total=False):
    """Vector store configuration."""
    collection_name: str
    embedding_model: str
    distance_metric: str


class AgentResponse(TypedDict, total=False):
    """Agent execution response."""
    response: str
    error: Optional[str]
    metadata: Optional[MetadataDict]
    session_id: Optional[str | int]


class AgentExecutionResult(TypedDict, total=False):
    """Complete agent execution result."""
    query: str
    response: str
    agent_type: str
    confidence: Optional[float]
    session_id: Optional[str | int]
    session_name: Optional[str]
    is_new_session: bool
    error: Optional[str]
    metadata: Optional[MetadataDict]


class NodeReturnType(TypedDict, total=False):
    """Return type for agent workflow nodes.
    
    This represents the partial state updates that nodes can return.
    Each node can update specific fields without needing to return all state.
    """
    response: Optional[str]
    error: Optional[str]
    thinking: Optional[str]
    plan: Optional[dict[str, Any]]
    schema: Optional[dict[str, Any]]
    cypher_query: Optional[str]
    validation: Optional[dict[str, Any]]
    results: Optional[list[dict[str, Any]]]
    attempt: Optional[int]
    should_retry: Optional[bool]
    skip_retry: Optional[bool]
    evaluation: Optional[str]
    execution_error: Optional[str]
    validation_passed: Optional[bool]
    retrieved_docs: Optional[list[tuple[Any, float]]]
    reranked_docs: Optional[list[tuple[Any, float]]]
    answer: Optional[str]
    context_used: Optional[int]
    retrieval_count: Optional[int]
    metadata_filter: Optional[dict[str, Any]]
