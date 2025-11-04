from fastapi import APIRouter, Depends, status, HTTPException
from app.services.document import DocumentService
from app.schemas.document import DocumentCreate, DocumentResponse
from app.database.session import get_db_session
from app.exceptions.base import NotFoundException
from app.exceptions.database import DatabaseException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    request: DocumentCreate,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        service = DocumentService(session)
        return await service.create_document(request)
    except DatabaseException as e:
        logger.error(f"Database error in create_document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        service = DocumentService(session)
        return await service.get_by_id(document_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error in get_document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/{user_id}", response_model=List[DocumentResponse])
async def get_user_documents(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        service = DocumentService(session)
        return await service.get_by_user(user_id, skip, limit)
    except DatabaseException as e:
        logger.error(f"Database error in get_user_documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_user_documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        service = DocumentService(session)
        await service.delete_document(document_id)
    except DatabaseException as e:
        logger.error(f"Database error in delete_document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
