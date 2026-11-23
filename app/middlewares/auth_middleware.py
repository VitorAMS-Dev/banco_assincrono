"""Dependency do FastAPI para validação de JWT em rotas protegidas."""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.exceptions.custom_exceptions import TokenInvalido

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


async def get_current_cliente_id(token: str | None = Depends(oauth2_scheme)) -> str:
    if not token:
        raise TokenInvalido("Token de autenticação não fornecido.")
    payload = decode_access_token(token)
    cliente_id = payload.get("sub")
    if not cliente_id:
        raise TokenInvalido("Token inválido: subject ausente.")
    return cliente_id
