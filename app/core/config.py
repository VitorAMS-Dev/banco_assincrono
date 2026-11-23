"""
Configurações centrais da aplicação.
Lê variáveis de ambiente e expõe um objeto Settings único (singleton via lru_cache).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "Bank Async API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database (PostgreSQL assíncrono via asyncpg)
    DATABASE_URL: str = "postgresql+asyncpg://bank_user:bank_pass@db:5432/bank_db"
    DATABASE_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL_SECONDS: int = 30

    # JWT
    JWT_SECRET_KEY: str = "CHANGE_ME_super_secret_key_for_jwt_signing"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Timeouts
    OPERATION_TIMEOUT_SECONDS: int = 30

    # Webhook / notificação assíncrona (httpx.AsyncClient)
    NOTIFICATION_WEBHOOK_URL: str | None = None

    # Seed
    SEED_ON_STARTUP: bool = True
    SEED_CLIENTES: int = 20
    SEED_CONTAS: int = 20
    SEED_TRANSACOES: int = 100

    # Logs
    LOG_DIR: str = "logs"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
