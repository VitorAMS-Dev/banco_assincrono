"""
Fixtures compartilhadas dos testes.
Usa SQLite assíncrono (aiosqlite) isolado por teste, para não depender de um
PostgreSQL real durante a suíte automatizada (em produção a app usa asyncpg).
"""
import asyncio
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SEED_ON_STARTUP"] = "false"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # cache falha graciosamente se indisponível

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import session as db_session
from main import app as fastapi_app

# Engine único compartilhado em memória para toda a suíte (StaticPool mantém a
# mesma conexão SQLite viva entre operações assíncronas).
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

# Faz a aplicação usar o engine/sessão de teste em vez do PostgreSQL real.
db_session.engine = test_engine
db_session.AsyncSessionLocal = TestSessionLocal


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(db_session.Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(db_session.Base.metadata.drop_all)


async def _override_get_db():
    async with TestSessionLocal() as session:
        yield session


from app.database.session import get_db
from app.api.deps import get_session

fastapi_app.dependency_overrides[get_db] = _override_get_db
fastapi_app.dependency_overrides[get_session] = _override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
