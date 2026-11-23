"""
Configuração centralizada de logging.
Gera 4 arquivos de log em logs/: app.log, error.log, access.log, database.log
Todos os handlers são thread-safe (RotatingFileHandler) e seguros para uso
a partir de código assíncrono, já que o logging em si não bloqueia o event
loop de forma relevante para esta aplicação (operações de I/O em disco são
rápidas e bufferizadas pelo sistema operacional).
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from app.core.config import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def _build_logger(name: str, filename: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.handlers:
        return logger  # evita handlers duplicados em reload

    file_path = os.path.join(settings.LOG_DIR, filename)
    handler = RotatingFileHandler(file_path, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)

    if settings.DEBUG:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console)

    logger.propagate = False
    return logger


app_logger = _build_logger("bank.app", "app.log")
error_logger = _build_logger("bank.error", "error.log", level=logging.ERROR)
access_logger = _build_logger("bank.access", "access.log")
database_logger = _build_logger("bank.database", "database.log")
