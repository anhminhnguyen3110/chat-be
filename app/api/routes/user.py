from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...schemas.user import UserCreate, UserResponse
from ...services.user import UserService
from ...database.session import get_db_session
from ...exceptions.base import NotFoundException
from ...exceptions.database import DatabaseException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    request: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        service = UserService(session)
        return await service.create_user(request)
    except DatabaseException as e:
        logger.error(f"Database error in create_user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        service = UserService(session)
        return await service.get_by_id(user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error in get_user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        service = UserService(session)
        return await service.get_all(skip, limit)
    except DatabaseException as e:
        logger.error(f"Database error in get_all_users: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_all_users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
