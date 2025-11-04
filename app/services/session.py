"""Session service for managing user sessions."""

from app.repositories.session import SessionRepository
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate, GroupedSessionsResponse
from app.models.session import Session
from app.exceptions.base import NotFoundException
from app.exceptions.database import DatabaseException
from app.constants.messages import Messages
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging
from datetime import datetime, timedelta, timezone
from app.ai_core.agents.agent_factory import AgentFactory, AgentType

logger = logging.getLogger(__name__)


class SessionService:
    """Service for session-related operations."""
    
    def __init__(self, session: AsyncSession):
        self.repository = SessionRepository(session)
    
    async def create_session(self, session_data: SessionCreate) -> SessionResponse:
        """Create a new session."""
        try:
            session_obj = Session(
                name=session_data.name,
                user_id=session_data.user_id
            )
            
            created = await self.repository.create(session_obj)
            return SessionResponse.model_validate(created)
        except SQLAlchemyError as e:
            logger.error(f"Database error creating session: {e}")
            raise DatabaseException(f"Failed to create session: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating session: {e}")
            raise
    
    async def get_by_id(self, session_id: int) -> SessionResponse:
        """Get a session by ID."""
        try:
            session_obj = await self.repository.get_by_id(session_id)
            if not session_obj:
                raise NotFoundException(Messages.SESSION_NOT_FOUND, "Session")
            return SessionResponse.model_validate(session_obj)
        except NotFoundException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error getting session {session_id}: {e}")
            raise DatabaseException(f"Failed to get session: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting session {session_id}: {e}")
            raise
    
    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[SessionResponse]:
        """Get all sessions for a user."""
        try:
            sessions = await self.repository.get_by_user_id(user_id, skip, limit)
            return [SessionResponse.model_validate(s) for s in sessions]
        except SQLAlchemyError as e:
            logger.error(f"Database error getting sessions for user {user_id}: {e}")
            raise DatabaseException(f"Failed to get sessions: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting sessions for user {user_id}: {e}")
            raise
    
    async def get_by_user_grouped(self, user_id: int, limit: int = 30) -> GroupedSessionsResponse:
        """
        Get sessions for a user grouped by time periods.
        
        Groups sessions into:
        - Today
        - Yesterday
        - Last 7 days (excluding today & yesterday)
        - Last 30 days (excluding above)
        - Older (beyond 30 days)
        
        Returns up to 'limit' sessions per group.
        """
        try:
            all_sessions = await self.repository.get_by_user_id(user_id, skip=0, limit=1000)
            
            now = datetime.now(timezone.utc)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_start = today_start - timedelta(days=1)
            seven_days_ago = today_start - timedelta(days=7)
            thirty_days_ago = today_start - timedelta(days=30)
            
            today_sessions = []
            yesterday_sessions = []
            last_7_days_sessions = []
            last_30_days_sessions = []
            older_sessions = []
            
            for session in all_sessions:
                session_response = SessionResponse.model_validate(session)
                
                created_at = session.created_at
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                
                if created_at >= today_start:
                    if len(today_sessions) < limit:
                        today_sessions.append(session_response)
                elif created_at >= yesterday_start:
                    if len(yesterday_sessions) < limit:
                        yesterday_sessions.append(session_response)
                elif created_at >= seven_days_ago:
                    if len(last_7_days_sessions) < limit:
                        last_7_days_sessions.append(session_response)
                elif created_at >= thirty_days_ago:
                    if len(last_30_days_sessions) < limit:
                        last_30_days_sessions.append(session_response)
                else:
                    if len(older_sessions) < limit:
                        older_sessions.append(session_response)
        
            return GroupedSessionsResponse(
                today=today_sessions,
                yesterday=yesterday_sessions,
                last_7_days=last_7_days_sessions,
                last_30_days=last_30_days_sessions,
                older=older_sessions,
                total=len(all_sessions)
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting grouped sessions for user {user_id}: {e}")
            raise DatabaseException(f"Failed to get grouped sessions: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting grouped sessions for user {user_id}: {e}")
            raise
    
    async def update_session(self, session_id: int, session_data: SessionUpdate) -> SessionResponse:
        """Update a session."""
        try:
            session_obj = await self.repository.get_by_id(session_id)
            if not session_obj:
                raise NotFoundException(Messages.SESSION_NOT_FOUND, "Session")
            
            if session_data.name is not None:
                session_obj.name = session_data.name
            
            updated = await self.repository.update(session_obj)
            return SessionResponse.model_validate(updated)
        except NotFoundException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error updating session {session_id}: {e}")
            raise DatabaseException(f"Failed to update session: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating session {session_id}: {e}")
            raise
    
    async def delete_session(self, session_id: int) -> bool:
        """Delete a session and its checkpoints."""
        try:
            try:
                agent = AgentFactory.create(AgentType.CHAT)
                await agent.clear_session_history(str(session_id))
                logger.info(f"Cleared checkpoints for session {session_id}")
            except Exception as e:
                logger.warning(f"Failed to clear checkpoints for session {session_id}: {e}")
            
            return await self.repository.delete(session_id)
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting session {session_id}: {e}")
            raise DatabaseException(f"Failed to delete session: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting session {session_id}: {e}")
            raise
