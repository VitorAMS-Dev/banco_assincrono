"""Repositório assíncrono para a entidade Conta."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conta import Conta


class ContaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, conta_id: str) -> Conta | None:
        result = await self.session.execute(select(Conta).where(Conta.id == conta_id))
        return result.scalar_one_or_none()

    async def get_by_id_for_update(self, conta_id: str) -> Conta | None:
        """Busca a conta com lock otimista via refresh após commit (compatível com SQLite/Postgres)."""
        result = await self.session.execute(select(Conta).where(Conta.id == conta_id).with_for_update())
        return result.scalar_one_or_none()

    async def get_by_numero(self, numero: str) -> Conta | None:
        result = await self.session.execute(select(Conta).where(Conta.numero == numero))
        return result.scalar_one_or_none()

    async def list_by_cliente(self, cliente_id: str) -> list[Conta]:
        result = await self.session.execute(select(Conta).where(Conta.cliente_id == cliente_id))
        return list(result.scalars().all())

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Conta]:
        result = await self.session.execute(select(Conta).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, conta: Conta) -> Conta:
        self.session.add(conta)
        await self.session.commit()
        await self.session.refresh(conta)
        return conta

    async def save(self, conta: Conta) -> Conta:
        await self.session.commit()
        await self.session.refresh(conta)
        return conta
