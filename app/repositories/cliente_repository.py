"""Repositório assíncrono para a entidade Cliente."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente


class ClienteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, cliente_id: str) -> Cliente | None:
        result = await self.session.execute(select(Cliente).where(Cliente.id == cliente_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Cliente | None:
        result = await self.session.execute(select(Cliente).where(Cliente.email == email))
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Cliente | None:
        result = await self.session.execute(select(Cliente).where(Cliente.cpf == cpf))
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Cliente]:
        result = await self.session.execute(select(Cliente).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, cliente: Cliente) -> Cliente:
        self.session.add(cliente)
        await self.session.commit()
        await self.session.refresh(cliente)
        return cliente
