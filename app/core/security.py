"""
Segurança: hashing de senha (bcrypt via passlib) e geração/validação de JWT.
Funções de I/O criptográfico de hashing são CPU-bound; expomos versões async
que delegam ao executor padrão para não bloquear o event loop em cargas altas.
"""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt, JWTError

from app.core.config import settings
from app.exceptions.custom_exceptions import TokenInvalido


def _hash_password_sync(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt())
    return hashed.decode("utf-8")


def _verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(_hash_password_sync, password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(_verify_password_sync, plain_password, hashed_password)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": subject, "iat": now, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise TokenInvalido("Token inválido ou expirado.") from exc
