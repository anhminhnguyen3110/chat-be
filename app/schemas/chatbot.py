from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
from app.constants.enums import MessageRole
from app.types.common import MetadataDict
from app.types.guardrail import GuardrailValidationResult


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class StreamChunk(BaseModel):
    """Streaming response chunk with type."""
    type: Literal["chunk", "error", "done"]
    content: str
    metadata: Optional[MetadataDict] = None


class ChatRequest(BaseModel):
    """Request for smart chat with agent routing."""
    query: str
    session_id: Optional[int | str] = None  # Accept both int and string


class ChatResponse(BaseModel):
    """Response from smart chat."""
    query: str
    response: str
    agent_type: Optional[str] = None
    confidence: Optional[float] = None
    session_id: Optional[int | str] = None  # Return int or string
    session_name: Optional[str] = None  # Session name for newly created sessions
    is_new_session: Optional[bool] = False  # Indicates if this is a newly created session
    error: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    query: str
    session_id: Optional[int | str] = None


class ChatCompletionResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    guardrail_result: Optional[GuardrailValidationResult] = None


class DeleteMessagesRequest(BaseModel):
    session_id: str
    message_ids: Optional[List[int]] = None

