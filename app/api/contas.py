"""Rotas de contas: criação, saldo, bloqueio, encerramento."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.conta_schema import ContaCreate, ContaOut, SaldoOut
from app.services.conta_service import ContaService

router = APIRouter(prefix="/api/v1/contas", tags=["Contas"])


@router.post("", response_model=ContaOut, status_code=status.HTTP_201_CREATED)
async def criar_conta(data: ContaCreate, session: AsyncSession = Depends(get_session)):
    service = ContaService(session)
    conta = await service.criar_conta(data.cliente_id)
    return ContaOut.model_validate(conta)


@router.get("/{conta_id}", response_model=ContaOut)
async def obter_conta(conta_id: str, session: AsyncSession = Depends(get_session)):
    service = ContaService(session)
    conta = await service.buscar_por_id(conta_id)
    return ContaOut.model_validate(conta)


@router.get("/{conta_id}/saldo", response_model=SaldoOut)
async def consultar_saldo(conta_id: str, session: AsyncSession = Depends(get_session)):
    service = ContaService(session)
    saldo = await service.consultar_saldo(conta_id)
    return SaldoOut(conta_id=conta_id, saldo=saldo)


@router.patch("/{conta_id}/bloquear", response_model=ContaOut)
async def bloquear_conta(conta_id: str, session: AsyncSession = Depends(get_session)):
    service = ContaService(session)
    conta = await service.bloquear_conta(conta_id)
    return ContaOut.model_validate(conta)


@router.patch("/{conta_id}/desbloquear", response_model=ContaOut)
async def desbloquear_conta(conta_id: str, session: AsyncSession = Depends(get_session)):
    service = ContaService(session)
    conta = await service.desbloquear_conta(conta_id)
    return ContaOut.model_validate(conta)


@router.delete("/{conta_id}", response_model=ContaOut)
async def encerrar_conta(conta_id: str, session: AsyncSession = Depends(get_session)):
    service = ContaService(session)
    conta = await service.encerrar_conta(conta_id)
    return ContaOut.model_validate(conta)


@router.get("/cliente/{cliente_id}", response_model=list[ContaOut])
async def listar_contas_por_cliente(cliente_id: str, session: AsyncSession = Depends(get_session)):
    service = ContaService(session)
    contas = await service.listar_por_cliente(cliente_id)
    return [ContaOut.model_validate(c) for c in contas]
