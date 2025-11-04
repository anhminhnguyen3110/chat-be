"""Neo4j agent state definition."""

from typing import Optional, List
from app.ai_core.agents.base.state import BaseAgentState
from app.types import Neo4jSchemaResult, Neo4jValidationResult


class Neo4jAgentState(BaseAgentState, total=False):
    """State for Neo4j agent workflow."""
    
    thinking: Optional[str]
    plan: Optional[dict]
    schema: Optional[Neo4jSchemaResult]
    cypher_query: Optional[str]
    validation: Optional[Neo4jValidationResult]
    explain: Optional[dict]
    results: Optional[List[dict]]
    attempts: Optional[int]
    success: Optional[bool]
    skip_retry: Optional[bool]
