from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import Optional
from sqlalchemy import text
import logging
from app.database.engine import engine


@asynccontextmanager
async def get_connection():
    async with engine.begin() as conn:
        yield conn


async def check_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
