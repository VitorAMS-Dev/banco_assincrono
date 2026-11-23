"""Rotas de autenticação."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.config import settings
from app.schemas.auth_schema import TokenResponse
from app.schemas.cliente_schema import ClienteLogin
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
async def login(data: ClienteLogin, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    token = await service.login(data.email, data.senha)
    return TokenResponse(access_token=token, expires_in_minutes=settings.JWT_EXPIRE_MINUTES)
