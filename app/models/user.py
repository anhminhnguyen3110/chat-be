from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    fullname = Column(String(255), nullable=False)
    
    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan"
    )

