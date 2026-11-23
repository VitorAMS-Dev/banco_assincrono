"""Dependências compartilhadas das rotas."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

DbSession = AsyncSession


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session
