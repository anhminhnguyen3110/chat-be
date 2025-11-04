"""Message service for managing session messages."""

from ..repositories.message import MessageRepository
from ..schemas.message import MessageCreate, MessageResponse
from ..models.message import Message
from ..exceptions.database import DatabaseException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class MessageService:
    """Service for message-related operations."""
    
    def __init__(self, session: AsyncSession):
        self.repository = MessageRepository(session)
    
    async def create_message(self, message_data: MessageCreate) -> MessageResponse:
        """Create a new message."""
        try:
            message = Message(
                content=message_data.content,
                role=message_data.role,
                session_id=message_data.session_id
            )
            
            created = await self.repository.create(message)
            return MessageResponse.model_validate(created)
        except SQLAlchemyError as e:
            logger.error(f"Database error creating message: {e}")
            raise DatabaseException(f"Failed to create message: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating message: {e}")
            raise
    
    async def get_by_session(self, session_id: int, limit: int = 20) -> List[MessageResponse]:
        """Get messages for a session (oldest first)."""
        try:
            messages = await self.repository.get_by_session_id(session_id, limit=limit)
            return [MessageResponse.model_validate(m) for m in messages]
        except SQLAlchemyError as e:
            logger.error(f"Database error getting messages for session {session_id}: {e}")
            raise DatabaseException(f"Failed to get messages: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting messages for session {session_id}: {e}")
            raise
    
    async def get_by_session_paginated(
        self, 
        session_id: int, 
        skip: int = 0,
        limit: int = 20
    ) -> List[MessageResponse]:
        """
        Get paginated messages for a session (newest first).
        
        Args:
            session_id: Session ID
            skip: Number of messages to skip
            limit: Number of messages to return
            
        Returns:
            List of messages ordered by created_at DESC
        """
        try:
            messages = await self.repository.get_by_session_id_paginated(
                session_id, skip, limit
            )
            return [MessageResponse.model_validate(m) for m in messages]
        except SQLAlchemyError as e:
            logger.error(f"Database error getting paginated messages for session {session_id}: {e}")
            raise DatabaseException(f"Failed to get messages: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting paginated messages for session {session_id}: {e}")
            raise
    
    async def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        try:
            return await self.repository.delete(message_id)
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting message {message_id}: {e}")
            raise DatabaseException(f"Failed to delete message: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting message {message_id}: {e}")
            raise

