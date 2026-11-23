"""Rotas de clientes."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.cliente_schema import ClienteCreate, ClienteOut
from app.services.cliente_service import ClienteService

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])


@router.post("", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
async def criar_cliente(data: ClienteCreate, session: AsyncSession = Depends(get_session)):
    service = ClienteService(session)
    cliente = await service.criar_cliente(data)
    return ClienteOut.model_validate(cliente)


@router.get("/{cliente_id}", response_model=ClienteOut)
async def obter_cliente(cliente_id: str, session: AsyncSession = Depends(get_session)):
    service = ClienteService(session)
    cliente = await service.buscar_por_id(cliente_id)
    return ClienteOut.model_validate(cliente)


@router.get("", response_model=list[ClienteOut])
async def listar_clientes(skip: int = 0, limit: int = 20, session: AsyncSession = Depends(get_session)):
    service = ClienteService(session)
    clientes = await service.listar(skip, limit)
    return [ClienteOut.model_validate(c) for c in clientes]
