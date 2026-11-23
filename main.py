"""
Ponto de entrada da API Bancária Assíncrona.
Cria as tabelas e popula o banco automaticamente no startup (lifespan async).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, clientes, contas, transacoes
from app.core.config import settings
from app.core.logging_config import app_logger
from app.database.seed import seed_database
from app.database.session import create_all_tables
from app.exceptions.handlers import register_exception_handlers
from app.middlewares.timing_middleware import TimingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Iniciando aplicação %s v%s", settings.APP_NAME, settings.APP_VERSION)
    await create_all_tables()
    if settings.SEED_ON_STARTUP:
        await seed_database()
    yield
    app_logger.info("Encerrando aplicação.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Bancária 100% assíncrona (FastAPI + AsyncIO + SQLAlchemy Async + PostgreSQL + Redis).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TimingMiddleware)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(contas.router)
app.include_router(transacoes.router)


@app.get("/", tags=["Health"])
async def root():
    return {"success": True, "message": f"{settings.APP_NAME} no ar.", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health(request: Request):
    return {"success": True, "status": "ok", "request_id": getattr(request.state, "request_id", None)}
