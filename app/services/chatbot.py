"""Chatbot service for smart chat with agent routing and DB persistence."""

from typing import AsyncGenerator, Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.ai_core.agents import AgentRouter
from app.ai_core.agents.agent_factory import AgentFactory, AgentType
from app.ai_core.llm import LLMFactory, LLMProviderType
from app.config.settings import settings
from langchain_core.messages import HumanMessage
from app.schemas.chatbot import ChatRequest, ChatResponse, ChatCompletionRequest, ChatCompletionResponse, StreamChunk
from app.schemas.message import MessageCreate
from app.schemas.session import SessionCreate
from app.repositories.session import SessionRepository
from app.repositories.message import MessageRepository
from app.repositories.user import UserRepository
from app.services.message import MessageService
from app.services.session import SessionService
from app.models.session import Session
from app.models.message import Message
from app.constants.enums import MessageRole
from app.exceptions.service import LLMException
from app.exceptions.database import DatabaseException
from app.exceptions.base import NotFoundException

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Unified chatbot service with agent intelligence and DB persistence.
    
    Features:
    - chat(): Smart chat with auto intent detection + DB save
    - chat_stream(): Streaming chat with auto detect + DB save
    - completion(): Raw LLM completion (no agent, no DB)
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        if session:
            self.router = AgentRouter()
            self.session_repo = SessionRepository(session)
            self.message_repo = MessageRepository(session)
            self.user_repo = UserRepository(session)
            self.session_service = SessionService(session)
            self.message_service = MessageService(session)
    
    async def chat(
        self,
        request: ChatRequest,
        user_id: int,
        confidence_threshold: float = 0.6
    ) -> ChatResponse:
        """
        Smart chat with automatic intent detection and DB persistence.
        
        Args:
            request: Chat request with query and optional history
            user_id: User ID for conversation tracking
            confidence_threshold: Minimum confidence for auto-routing
            
        Returns:
            ChatResponse with agent-generated response
        """
        logger.info(f"Chat request from user {user_id}: {request.query[:50]}...")
        
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise NotFoundException(f"User with ID {user_id} not found", "user")
            
            is_new_session = False
            session_obj = None
            
            if request.session_id:
                try:
                    session_int = int(request.session_id)
                    session_obj = await self.session_repo.get_by_id(session_int)
                    if not session_obj:
                        raise NotFoundException(f"Session with ID {session_int} not found", "session")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid session_id format: {request.session_id}")
                    raise NotFoundException("Invalid session ID format", "session")
            
            if not session_obj:
                session_obj = Session(
                    name=request.query[:50],
                    user_id=user_id
                )
                session_obj = await self.session_repo.create(session_obj)
                is_new_session = True
            
            await self._save_user_message(session_obj.id, request.query)
            
            history = await self._build_history(session_obj.id)
            
            result = await self.router.route(
                user_input=request.query,
                session_id=str(session_obj.id),
                user_id=user_id,
                agent_type=None,
                config={"history": history} if history else None,
                confidence_threshold=confidence_threshold
            )
            
            routing = result.get("_routing", {})
            agent_type = routing.get("agent_type")
            confidence = routing.get("confidence")
            
            response_text = result.get("response", "")
            
            await self._save_assistant_message(
                session_obj.id,
                response_text
            )
            
            return ChatResponse(
                query=request.query,
                response=response_text,
                agent_type=agent_type,
                confidence=confidence,
                session_id=str(session_obj.id),
                session_name=session_obj.name if is_new_session else None,
                is_new_session=is_new_session,
                error=result.get("error")
            )
            
        except NotFoundException:
            raise
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}", exc_info=True)
            return ChatResponse(
                query=request.query,
                response="I apologize, but I encountered an error processing your request.",
                error=str(e)
            )
    
    async def chat_stream(
        self,
        request: ChatRequest,
        user_id: int,
        confidence_threshold: float = 0.6
    ) -> AsyncGenerator[dict[str, any], None]:
        """
        REAL streaming chat with automatic intent detection and DB persistence.
        
        Args:
            request: Chat request with query and optional history
            user_id: User ID for conversation tracking
            confidence_threshold: Minimum confidence for auto-routing
            
        Yields:
            StreamChunk dict with type: "chunk" | "error" | "done"
        """
        logger.info(f"Stream chat request from user {user_id}: {request.query[:50]}...")
        
        try:
            is_new_session = False
            session_obj = None
            
            if request.session_id:
                try:
                    session_int = int(request.session_id)
                    session_obj = await self.session_repo.get_by_id(session_int)
                    if not session_obj:
                        raise NotFoundException(f"Session with ID {session_int} not found", "session")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid session_id format: {request.session_id}")
                    raise NotFoundException("Invalid session ID format", "session")
            
            if not session_obj:
                session_obj = Session(
                    name=request.query[:50],
                    user_id=user_id
                )
                session_obj = await self.session_repo.create(session_obj)
                is_new_session = True
            
            await self._save_user_message(session_obj.id, request.query)
            
            history = await self._build_history(session_obj.id)
            
            auto_routed = False
            confidence = 1.0
            agent_type_enum = None
            
            detected_type, confidence = await self.router.detect_intent(request.query)
            
            if confidence < confidence_threshold:
                logger.warning(
                    f"Low confidence ({confidence:.2f}) for {detected_type}, "
                    f"defaulting to CHAT agent"
                )
                agent_type_enum = AgentType.CHAT
            else:
                agent_type_enum = detected_type
                auto_routed = True
                logger.info(f"Auto-routed to {agent_type_enum} (confidence: {confidence:.2f})")
            
            agent = AgentFactory.create(agent_type_enum, config=None)
            
            full_response = ""
            async for token in agent.execute_stream(
                query=request.query,
                session_id=str(session_obj.id),
                user_id=user_id,
                history=history,
                system_prompt=None,
                metadata={
                    "session_id": str(session_obj.id),
                    "agent_type": agent_type_enum.value,
                    "auto_routed": auto_routed,
                    "confidence": confidence
                }
            ):
                full_response += token
                yield StreamChunk(
                    type="chunk",
                    content=token,
                    metadata={"agent_type": agent_type_enum.value}
                ).model_dump()
            
            await self._save_assistant_message(
                session_obj.id,
                full_response
            )
            
            yield StreamChunk(
                type="done",
                content="",
                metadata={
                    "session_id": str(session_obj.id),
                    "session_name": session_obj.name if is_new_session else None,
                    "is_new_session": is_new_session,
                    "agent_type": agent_type_enum.value,
                    "confidence": confidence
                }
            ).model_dump()
                
        except Exception as e:
            logger.error(f"Stream chat failed: {str(e)}", exc_info=True)
            yield StreamChunk(
                type="error",
                content=str(e),
                metadata={"error_type": type(e).__name__}
            ).model_dump()
    
    async def completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Raw LLM completion without agent routing or DB persistence."""
        logger.info(f"Completion request: {request.query[:50]}...")
        
        try:
            llm = LLMFactory.create(
                provider_type=LLMProviderType(settings.LLM_PROVIDER),
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                enable_guardrail=settings.ENABLE_GUARDRAIL
            )
            
            try:
                response = await llm.ainvoke([HumanMessage(content=request.query)])
            except ValueError as ve:
                return ChatCompletionResponse(
                    content=str(ve),
                    model=settings.LLM_MODEL,
                    guardrail_result={"valid": False, "reason": str(ve), "blocked": True}
                )
            
            return ChatCompletionResponse(
                content=response.content,
                model=settings.LLM_MODEL,
                usage={
                    "prompt_tokens": response.response_metadata.get("token_usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": response.response_metadata.get("token_usage", {}).get("completion_tokens", 0),
                    "total_tokens": response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
                },
                guardrail_result={"valid": True, "reason": None, "blocked": False}
            )
        except Exception as e:
            logger.error(f"Chat completion error: {str(e)}")
            raise LLMException(f"Chat completion failed: {str(e)}")
    
    async def _save_user_message(self, session_id: int, content: str) -> Message:
        """Save user message to DB."""
        try:
            message = Message(
                content=content,
                role=MessageRole.USER,
                session_id=session_id
            )
            return await self.message_repo.create(message)
        except SQLAlchemyError as e:
            logger.error(f"Database error saving user message: {e}")
            raise DatabaseException(f"Failed to save user message: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error saving user message: {e}")
            raise
    
    async def _save_assistant_message(
        self,
        session_id: int,
        content: str
    ) -> Message:
        """Save assistant message to DB."""
        try:
            message = Message(
                content=content,
                role=MessageRole.ASSISTANT,
                session_id=session_id
            )
            return await self.message_repo.create(message)
        except SQLAlchemyError as e:
            logger.error(f"Database error saving assistant message: {e}")
            raise DatabaseException(f"Failed to save assistant message: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error saving assistant message: {e}")
            raise
    
    async def _build_history(
        self,
        session_id: int
    ) -> List[Dict[str, str]]:
        """Build conversation history from DB."""
        try:
            messages = await self.message_repo.get_by_session_id(
                session_id,
                limit=20
            )
            
            return [
                {"role": msg.role.value, "content": msg.content}
                for msg in messages
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error building history: {e}")
            raise DatabaseException(f"Failed to build conversation history: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error building history: {e}")
            raise

