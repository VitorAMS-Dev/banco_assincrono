"""Serviço de regras de negócio para Conta (criação, saldo, bloqueio, encerramento)."""
import random
import string
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import ClienteNaoEncontrado, ContaNaoEncontrada, TransferenciaInvalida
from app.models.conta import Conta, StatusConta
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.conta_repository import ContaRepository
from app.services.cache_service import CacheService


def _gerar_numero_conta() -> str:
    return "".join(random.choices(string.digits, k=4)) + "-" + random.choice(string.digits)


class ContaService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ContaRepository(session)
        self.cliente_repo = ClienteRepository(session)
        self.cache = CacheService()

    async def criar_conta(self, cliente_id: str) -> Conta:
        cliente = await self.cliente_repo.get_by_id(cliente_id)
        if not cliente:
            raise ClienteNaoEncontrado("Cliente não encontrado.")

        numero = _gerar_numero_conta()
        while await self.repo.get_by_numero(numero):
            numero = _gerar_numero_conta()

        conta = Conta(numero=numero, cliente_id=cliente_id, saldo=Decimal("0.00"), status=StatusConta.ATIVA)
        return await self.repo.create(conta)

    async def buscar_por_id(self, conta_id: str) -> Conta:
        conta = await self.repo.get_by_id(conta_id)
        if not conta:
            raise ContaNaoEncontrada("Conta não encontrada.")
        return conta

    async def consultar_saldo(self, conta_id: str) -> Decimal:
        cache_key = f"saldo:{conta_id}"
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return Decimal(str(cached))

        conta = await self.buscar_por_id(conta_id)
        await self.cache.set(cache_key, str(conta.saldo))
        return Decimal(conta.saldo)

    async def bloquear_conta(self, conta_id: str) -> Conta:
        conta = await self.buscar_por_id(conta_id)
        conta.status = StatusConta.BLOQUEADA
        await self.repo.save(conta)
        await self.cache.delete(f"saldo:{conta_id}")
        return conta

    async def desbloquear_conta(self, conta_id: str) -> Conta:
        conta = await self.buscar_por_id(conta_id)
        conta.status = StatusConta.ATIVA
        await self.repo.save(conta)
        return conta

    async def encerrar_conta(self, conta_id: str) -> Conta:
        conta = await self.buscar_por_id(conta_id)
        if conta.saldo and Decimal(conta.saldo) != Decimal("0.00"):
            raise TransferenciaInvalida("Não é possível encerrar uma conta com saldo diferente de zero.")
        conta.status = StatusConta.ENCERRADA
        await self.repo.save(conta)
        await self.cache.delete(f"saldo:{conta_id}")
        return conta

    async def listar_por_cliente(self, cliente_id: str) -> list[Conta]:
        return await self.repo.list_by_cliente(cliente_id)
