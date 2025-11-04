from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    user = relationship("User", back_populates="documents")
    sessions = relationship(
        "Session",
        secondary="session_documents",
        back_populates="documents"
    )

