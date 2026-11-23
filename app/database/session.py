"""
Configuração do engine assíncrono SQLAlchemy 2.0 + asyncpg.
Nunca utiliza Session síncrona — toda a aplicação depende de AsyncSession.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

Base = declarative_base()

_engine_kwargs: dict = {"echo": settings.DATABASE_ECHO, "pool_pre_ping": True}

# SQLite (usado em testes locais) não suporta pool_size/max_overflow (usa NullPool).
# Em produção (PostgreSQL + asyncpg) o pool assíncrono completo é aplicado.
if not settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    _engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency do FastAPI: fornece uma AsyncSession por requisição."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def create_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
