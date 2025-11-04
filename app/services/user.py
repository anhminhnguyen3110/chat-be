"""User service for managing user operations."""

from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.exceptions.base import NotFoundException
from app.exceptions.database import DatabaseException
from app.constants.messages import Messages
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related operations."""
    
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        try:
            user = User(
                email=user_data.email,
                username=user_data.username,
                fullname=user_data.fullname
            )
            
            created = await self.repository.create(user)
            return UserResponse.model_validate(created)
        except SQLAlchemyError as e:
            logger.error(f"Database error creating user: {e}")
            raise DatabaseException(f"Failed to create user: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            raise
    
    async def get_by_id(self, user_id: int) -> UserResponse:
        """Get user by ID."""
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise NotFoundException(Messages.USER_NOT_FOUND, "User")
            return UserResponse.model_validate(user)
        except NotFoundException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user {user_id}: {e}")
            raise DatabaseException(f"Failed to get user: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting user {user_id}: {e}")
            raise
    
    async def get_by_email(self, email: str) -> UserResponse:
        """Get user by email."""
        try:
            user = await self.repository.get_by_email(email)
            if not user:
                raise NotFoundException(Messages.USER_NOT_FOUND, "User")
            return UserResponse.model_validate(user)
        except NotFoundException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by email {email}: {e}")
            raise DatabaseException(f"Failed to get user: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting user by email {email}: {e}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users with pagination."""
        try:
            users = await self.repository.find_all(skip, limit)
            return [UserResponse.model_validate(u) for u in users]
        except SQLAlchemyError as e:
            logger.error(f"Database error getting all users: {e}")
            raise DatabaseException(f"Failed to get users: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting all users: {e}")
            raise

