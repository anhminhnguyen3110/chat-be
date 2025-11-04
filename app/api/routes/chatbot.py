"""Chatbot API routes with unified agent-powered chat."""

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chatbot import ChatRequest, ChatResponse, ChatCompletionRequest, ChatCompletionResponse
from app.services.chatbot import ChatbotService
from app.core.streaming import StreamingResponse as SSEStreaming
from app.database.session import get_db_session
from app.exceptions.database import DatabaseException
from app.exceptions.base import NotFoundException
from app.config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chatbot"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: int = Query(..., description="User ID for session tracking"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Smart chat with automatic intent detection and DB persistence.
    
    Auto-routes to appropriate agent (Chat, Neo4j, RAG) based on query intent.
    Saves conversation and messages to database.
    """
    try:
        service = ChatbotService(session)
        return await service.chat(
            request=request,
            user_id=user_id,
            confidence_threshold=settings.AGENT_CONFIDENCE_THRESHOLD
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: int = Query(..., description="User ID for session tracking"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Streaming smart chat with automatic intent detection and DB persistence.
    
    Auto-routes to appropriate agent and streams response in chunks.
    Saves conversation and messages to database.
    """
    try:
        service = ChatbotService(session)
        
        async def event_stream():
            try:
                async for chunk in SSEStreaming.stream_generator(
                    service.chat_stream(
                        request=request,
                        user_id=user_id,
                        confidence_threshold=settings.AGENT_CONFIDENCE_THRESHOLD
                    )
                ):
                    yield chunk
            except Exception as e:
                logger.error(f"Error in chat_stream generator: {e}")
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat_stream: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/completion", response_model=ChatCompletionResponse)
async def completion(request: ChatCompletionRequest):
    """
    Raw LLM completion without agent routing or DB persistence.
    
    Direct LLM call with optional guardrail validation.
    No agent intelligence, no conversation history, no database save.
    """
    try:
        service = ChatbotService(None)  # No session needed for completion
        return await service.completion(request)
    except Exception as e:
        logger.error(f"Unexpected error in completion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

