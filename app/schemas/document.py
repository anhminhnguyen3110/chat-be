from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.schemas.base import BaseSchema, TimestampSchema


class DocumentBase(BaseSchema):
    title: str
    content: str


class DocumentCreate(BaseSchema):
    title: str
    content: str
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    user_id: int


class DocumentUpdate(BaseSchema):
    title: str | None = None
    content: str | None = None
    file_path: str | None = None
    file_type: str | None = None


class DocumentResponse(TimestampSchema):
    title: str
    content: str
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    user_id: int
