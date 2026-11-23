"""Serviço de autenticação: login e geração de JWT."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import access_logger
from app.core.security import create_access_token, verify_password
from app.exceptions.custom_exceptions import CredenciaisInvalidas
from app.repositories.cliente_repository import ClienteRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = ClienteRepository(session)

    async def login(self, email: str, senha: str) -> str:
        cliente = await self.repo.get_by_email(email)
        if not cliente or not await verify_password(senha, cliente.senha_hash):
            access_logger.warning("Tentativa de login falhou para email=%s", email)
            raise CredenciaisInvalidas("Email ou senha inválidos.")

        access_logger.info("Login bem-sucedido para cliente_id=%s", cliente.id)
        return create_access_token(subject=cliente.id, extra_claims={"email": cliente.email})
