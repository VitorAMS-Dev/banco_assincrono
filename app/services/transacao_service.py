"""
Serviço de transações financeiras: depósito, saque, transferência e extrato.
Todas as operações críticas são protegidas por asyncio.wait_for (timeout) e
registradas em log assíncrono. O cache de saldo é invalidado a cada escrita.
"""
import asyncio
from decimal import Decimal
from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging_config import app_logger
from app.exceptions.custom_exceptions import ContaBloqueada, SaldoInsuficiente, TransferenciaInvalida
from app.models.conta import StatusConta
from app.models.transacao import Transacao, TipoTransacao
from app.repositories.conta_repository import ContaRepository
from app.repositories.transacao_repository import TransacaoRepository
from app.schemas.transacao_schema import ExtratoOut, TransacaoOut
from app.services.cache_service import CacheService


class TransacaoService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.conta_repo = ContaRepository(session)
        self.transacao_repo = TransacaoRepository(session)
        self.cache = CacheService()

    def _validar_conta_ativa(self, conta) -> None:
        if conta.status != StatusConta.ATIVA:
            raise ContaBloqueada(f"Conta está {conta.status.value.lower()} e não pode realizar operações.")

    async def depositar(self, conta_id: str, valor: Decimal) -> Transacao:
        async def _executar():
            conta = await self.conta_repo.get_by_id(conta_id)
            if not conta:
                raise TransferenciaInvalida("Conta não encontrada.")
            self._validar_conta_ativa(conta)

            conta.saldo = Decimal(conta.saldo) + valor
            await self.conta_repo.save(conta)

            transacao = Transacao(conta_id=conta_id, tipo=TipoTransacao.DEPOSITO, valor=valor,
                                   descricao="Depósito em conta")
            transacao = await self.transacao_repo.create(transacao)
            await self.cache.delete(f"saldo:{conta_id}")
            app_logger.info("Depósito de %s na conta %s", valor, conta_id)
            return transacao

        return await asyncio.wait_for(_executar(), timeout=settings.OPERATION_TIMEOUT_SECONDS)

    async def sacar(self, conta_id: str, valor: Decimal) -> Transacao:
        async def _executar():
            conta = await self.conta_repo.get_by_id(conta_id)
            if not conta:
                raise TransferenciaInvalida("Conta não encontrada.")
            self._validar_conta_ativa(conta)

            saldo_atual = Decimal(conta.saldo)
            if saldo_atual < valor:
                raise SaldoInsuficiente("Saldo insuficiente para realizar o saque.")

            conta.saldo = saldo_atual - valor
            await self.conta_repo.save(conta)

            transacao = Transacao(conta_id=conta_id, tipo=TipoTransacao.SAQUE, valor=valor,
                                   descricao="Saque em conta")
            transacao = await self.transacao_repo.create(transacao)
            await self.cache.delete(f"saldo:{conta_id}")
            app_logger.info("Saque de %s na conta %s", valor, conta_id)
            return transacao

        return await asyncio.wait_for(_executar(), timeout=settings.OPERATION_TIMEOUT_SECONDS)

    async def transferir(self, conta_origem_id: str, conta_destino_id: str, valor: Decimal) -> Transacao:
        async def _executar():
            if conta_origem_id == conta_destino_id:
                raise TransferenciaInvalida("Conta de origem e destino não podem ser a mesma.")

            origem = await self.conta_repo.get_by_id(conta_origem_id)
            destino = await self.conta_repo.get_by_id(conta_destino_id)
            if not origem or not destino:
                raise TransferenciaInvalida("Conta de origem ou destino não encontrada.")

            self._validar_conta_ativa(origem)
            self._validar_conta_ativa(destino)

            saldo_origem = Decimal(origem.saldo)
            if saldo_origem < valor:
                raise SaldoInsuficiente("Saldo insuficiente para realizar a transferência.")

            origem.saldo = saldo_origem - valor
            destino.saldo = Decimal(destino.saldo) + valor

            await self.conta_repo.save(origem)
            await self.conta_repo.save(destino)

            transacao_envio = Transacao(
                conta_id=conta_origem_id,
                conta_destino_id=conta_destino_id,
                tipo=TipoTransacao.TRANSFERENCIA_ENVIADA,
                valor=valor,
                descricao=f"Transferência enviada para conta {destino.numero}",
            )
            transacao_recebimento = Transacao(
                conta_id=conta_destino_id,
                conta_destino_id=conta_origem_id,
                tipo=TipoTransacao.TRANSFERENCIA_RECEBIDA,
                valor=valor,
                descricao=f"Transferência recebida da conta {origem.numero}",
            )
            await self.transacao_repo.create(transacao_envio)
            await self.transacao_repo.create(transacao_recebimento)

            await self.cache.delete(f"saldo:{conta_origem_id}")
            await self.cache.delete(f"saldo:{conta_destino_id}")
            app_logger.info("Transferência de %s da conta %s para %s", valor, conta_origem_id, conta_destino_id)
            return transacao_envio

        return await asyncio.wait_for(_executar(), timeout=settings.OPERATION_TIMEOUT_SECONDS)

    async def extrato(self, conta_id: str, pagina: int = 1, tamanho_pagina: int = 20) -> ExtratoOut:
        conta = await self.conta_repo.get_by_id(conta_id)
        if not conta:
            raise TransferenciaInvalida("Conta não encontrada.")

        skip = (pagina - 1) * tamanho_pagina
        transacoes = await self.transacao_repo.list_by_conta(conta_id, skip=skip, limit=tamanho_pagina)
        total = await self.transacao_repo.count_by_conta(conta_id)

        return ExtratoOut(
            conta_id=conta_id,
            saldo_atual=Decimal(conta.saldo),
            transacoes=[TransacaoOut.model_validate(t) for t in transacoes],
            pagina=pagina,
            tamanho_pagina=tamanho_pagina,
            total=total,
        )
