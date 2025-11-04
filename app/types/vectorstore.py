"""Vector store related type definitions."""

from typing import TypedDict, Optional, Any


class VectorStoreConfig(TypedDict, total=False):
    """Configuration for vector store."""
    collection_name: str
    embedding_model: str
    embedding_dimension: int
    distance_metric: str
    connection_string: Optional[str]


class VectorStoreFilter(TypedDict, total=False):
    """Filter for vector store queries."""
    session_id: Optional[str | int]
    user_id: Optional[str]
    document_type: Optional[str]
    tags: Optional[list[str]]
    metadata: Optional[dict[str, Any]]
    date_from: Optional[str]
    date_to: Optional[str]


class VectorStoreStats(TypedDict, total=False):
    """Statistics about vector store."""
    total_documents: int
    total_embeddings: int
    collection_name: str
    embedding_dimension: int
    last_updated: Optional[str]


class DocumentWithScore(TypedDict):
    """Document with similarity score."""
    content: str
    metadata: dict[str, Any]
    score: float
    id: Optional[str]
