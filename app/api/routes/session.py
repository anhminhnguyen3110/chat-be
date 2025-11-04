from fastapi import APIRouter, Depends, Query, status, HTTPException
from ...services.session import SessionService
from ...services.message import MessageService
from ...schemas.session import SessionCreate, SessionResponse, SessionUpdate, GroupedSessionsResponse
from ...schemas.message import MessageResponse
from ...database.session import get_db_session
from ...exceptions.base import NotFoundException
from ...exceptions.database import DatabaseException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: SessionCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new session."""
    try:
        service = SessionService(session)
        return await service.create_session(request)
    except DatabaseException as e:
        logger.error(f"Database error in create_session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Get a session by ID."""
    # Validate ID range
    if session_id <= 0 or session_id > 2147483647:  # int32 max
        raise HTTPException(status_code=422, detail="Invalid session ID")
    
    try:
        service = SessionService(session)
        return await service.get_by_id(session_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error in get_session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/{user_id}/grouped", response_model=GroupedSessionsResponse)
async def get_user_sessions_grouped(
    user_id: int,
    limit: int = Query(30, ge=1, le=100, description="Max sessions per time group"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get all sessions for a user grouped by time periods.
    
    Groups sessions into: Today, Yesterday, Last 7 days, Last 30 days, Older.
    Each group shows up to 'limit' sessions.
    """
    try:
        service = SessionService(session)
        return await service.get_by_user_grouped(user_id, limit)
    except DatabaseException as e:
        logger.error(f"Database error in get_user_sessions_grouped: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_user_sessions_grouped: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    request: SessionUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a session."""
    try:
        service = SessionService(session)
        return await service.update_session(session_id, request)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error in update_session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in update_session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a session."""
    try:
        service = SessionService(session)
        await service.delete_session(session_id)
    except DatabaseException as e:
        logger.error(f"Database error in delete_session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Messages per page"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get messages for a session with pagination.
    
    Messages are ordered by created_at DESC (newest first).
    Use page parameter to load older messages.
    
    Example:
    - Page 1: GET /sessions/1/messages?page=1&limit=20 → Latest 20 messages
    - Page 2: GET /sessions/1/messages?page=2&limit=20 → Next 20 older messages
    """
    try:
        message_service = MessageService(session)
        skip = (page - 1) * limit
        return await message_service.get_by_session_paginated(session_id, skip=skip, limit=limit)
    except DatabaseException as e:
        logger.error(f"Database error in get_session_messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_session_messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
