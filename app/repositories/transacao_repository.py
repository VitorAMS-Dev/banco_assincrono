"""Repositório assíncrono para a entidade Transacao."""
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transacao import Transacao


class TransacaoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, transacao: Transacao) -> Transacao:
        self.session.add(transacao)
        await self.session.commit()
        await self.session.refresh(transacao)
        return transacao

    async def list_by_conta(self, conta_id: str, skip: int = 0, limit: int = 20) -> list[Transacao]:
        result = await self.session.execute(
            select(Transacao)
            .where(Transacao.conta_id == conta_id)
            .order_by(desc(Transacao.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_conta(self, conta_id: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Transacao).where(Transacao.conta_id == conta_id)
        )
        return int(result.scalar_one())
