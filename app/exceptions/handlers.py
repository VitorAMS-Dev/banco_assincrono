"""Registro de exception handlers globais no app FastAPI."""
import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging_config import error_logger
from app.exceptions.custom_exceptions import BankAPIException, DatabaseException, TimeoutException


def _error_body(message: str) -> dict:
    return {"success": False, "message": message}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BankAPIException)
    async def bank_exception_handler(request: Request, exc: BankAPIException):
        error_logger.error("BankAPIException em %s: %s", request.url.path, exc.message)
        return JSONResponse(status_code=exc.status_code, content=_error_body(exc.message))

    @app.exception_handler(asyncio.TimeoutError)
    async def timeout_handler(request: Request, exc: asyncio.TimeoutError):
        error_logger.error("Timeout em %s", request.url.path)
        timeout_exc = TimeoutException("Operação cancelada por tempo excedido.")
        return JSONResponse(status_code=timeout_exc.status_code, content=_error_body(timeout_exc.message))

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        error_logger.error("Erro de banco em %s: %s", request.url.path, str(exc))
        db_exc = DatabaseException("Erro ao acessar o banco de dados.")
        return JSONResponse(status_code=db_exc.status_code, content=_error_body(db_exc.message))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        error_logger.error("Erro não tratado em %s: %s", request.url.path, str(exc))
        return JSONResponse(status_code=500, content=_error_body("Erro interno do servidor."))
