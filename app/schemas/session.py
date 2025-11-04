from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas.base import BaseSchema, TimestampSchema


class SessionBase(BaseSchema):
    """Base session schema with common fields."""
    name: str = Field(..., max_length=255)


class SessionCreate(BaseSchema):
    """Schema for creating a new session."""
    name: str = Field(..., max_length=255)
    user_id: int
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError('user_id must be positive')
        if v > 2147483647:  # int32 max
            raise ValueError('user_id exceeds maximum value')
        return v


class SessionUpdate(BaseSchema):
    """Schema for updating a session."""
    name: str | None = Field(None, max_length=255)


class SessionResponse(TimestampSchema):
    """Schema for session response."""
    id: int
    name: str
    user_id: int
    
    class Config:
        from_attributes = True


class GroupedSessionsResponse(BaseSchema):
    """Schema for grouped sessions by time period."""
    today: List[SessionResponse] = []
    yesterday: List[SessionResponse] = []
    last_7_days: List[SessionResponse] = []
    last_30_days: List[SessionResponse] = []
    older: List[SessionResponse] = []
    total: int
