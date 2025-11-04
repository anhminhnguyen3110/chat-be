"""Document service for managing user documents."""

from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentResponse
from app.models.document import Document
from app.exceptions.base import NotFoundException
from app.exceptions.database import DatabaseException
from app.constants.messages import Messages
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document-related operations."""
    
    def __init__(self, session: AsyncSession):
        self.repository = DocumentRepository(session)
    
    async def create_document(self, document_data: DocumentCreate) -> DocumentResponse:
        """Create a new document."""
        try:
            document = Document(
                title=document_data.title,
                content=document_data.content,
                file_path=document_data.file_path,
                file_type=document_data.file_type,
                user_id=document_data.user_id
            )
            
            created = await self.repository.create(document)
            return DocumentResponse.model_validate(created)
        except SQLAlchemyError as e:
            logger.error(f"Database error creating document: {e}")
            raise DatabaseException(f"Failed to create document: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating document: {e}")
            raise
    
    async def get_by_id(self, document_id: int) -> DocumentResponse:
        """Get a document by ID."""
        try:
            document = await self.repository.get_by_id(document_id)
            if not document:
                raise NotFoundException(Messages.DOCUMENT_NOT_FOUND, "Document")
            return DocumentResponse.model_validate(document)
        except NotFoundException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error getting document {document_id}: {e}")
            raise DatabaseException(f"Failed to get document: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting document {document_id}: {e}")
            raise
    
    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[DocumentResponse]:
        """Get all documents for a user."""
        try:
            documents = await self.repository.get_by_user_id(user_id, skip, limit)
            return [DocumentResponse.model_validate(d) for d in documents]
        except SQLAlchemyError as e:
            logger.error(f"Database error getting documents for user {user_id}: {e}")
            raise DatabaseException(f"Failed to get documents: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting documents for user {user_id}: {e}")
            raise
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete a document."""
        try:
            return await self.repository.delete(document_id)
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting document {document_id}: {e}")
            raise DatabaseException(f"Failed to delete document: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting document {document_id}: {e}")
            raise

