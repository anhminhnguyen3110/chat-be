from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])

# Messages are accessed through /sessions/{session_id}/messages endpoint
# This router is kept for future message-specific operations
