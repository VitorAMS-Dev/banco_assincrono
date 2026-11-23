"""Rotas de transações financeiras: depósito, saque, transferência, extrato/histórico."""
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.conta_schema import DepositoRequest, SaqueRequest, TransferenciaRequest
from app.schemas.transacao_schema import ExtratoOut, TransacaoOut
from app.services.transacao_service import TransacaoService
from app.utils.notifier import notify_webhook

router = APIRouter(prefix="/api/v1/transacoes", tags=["Transações"])


@router.post("/deposito", response_model=TransacaoOut)
async def depositar(
    data: DepositoRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    service = TransacaoService(session)
    transacao = await service.depositar(data.conta_id, data.valor)
    background_tasks.add_task(notify_webhook, "deposito", {"conta_id": data.conta_id, "valor": str(data.valor)})
    return TransacaoOut.model_validate(transacao)


@router.post("/saque", response_model=TransacaoOut)
async def sacar(
    data: SaqueRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    service = TransacaoService(session)
    transacao = await service.sacar(data.conta_id, data.valor)
    background_tasks.add_task(notify_webhook, "saque", {"conta_id": data.conta_id, "valor": str(data.valor)})
    return TransacaoOut.model_validate(transacao)


@router.post("/transferencia", response_model=TransacaoOut)
async def transferir(
    data: TransferenciaRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    service = TransacaoService(session)
    transacao = await service.transferir(data.conta_origem_id, data.conta_destino_id, data.valor)
    background_tasks.add_task(
        notify_webhook,
        "transferencia",
        {"origem": data.conta_origem_id, "destino": data.conta_destino_id, "valor": str(data.valor)},
    )
    return TransacaoOut.model_validate(transacao)


@router.get("/extrato/{conta_id}", response_model=ExtratoOut)
async def extrato(
    conta_id: str,
    pagina: int = 1,
    tamanho_pagina: int = 20,
    session: AsyncSession = Depends(get_session),
):
    service = TransacaoService(session)
    return await service.extrato(conta_id, pagina, tamanho_pagina)


@router.get("/historico/{conta_id}", response_model=ExtratoOut)
async def historico(
    conta_id: str,
    pagina: int = 1,
    tamanho_pagina: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """Alias de /extrato — histórico completo paginado de transações da conta."""
    service = TransacaoService(session)
    return await service.extrato(conta_id, pagina, tamanho_pagina)
