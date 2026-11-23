"""Serviço de regras de negócio para Cliente."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.exceptions.custom_exceptions import ClienteJaExiste, ClienteNaoEncontrado
from app.models.cliente import Cliente
from app.repositories.cliente_repository import ClienteRepository
from app.schemas.cliente_schema import ClienteCreate


class ClienteService:
    def __init__(self, session: AsyncSession):
        self.repo = ClienteRepository(session)

    async def criar_cliente(self, data: ClienteCreate) -> Cliente:
        if await self.repo.get_by_email(data.email) or await self.repo.get_by_cpf(data.cpf):
            raise ClienteJaExiste("Já existe um cliente com este email ou CPF.")

        senha_hash = await hash_password(data.senha)
        cliente = Cliente(nome=data.nome, cpf=data.cpf, email=data.email, senha_hash=senha_hash)
        return await self.repo.create(cliente)

    async def buscar_por_id(self, cliente_id: str) -> Cliente:
        cliente = await self.repo.get_by_id(cliente_id)
        if not cliente:
            raise ClienteNaoEncontrado("Cliente não encontrado.")
        return cliente

    async def listar(self, skip: int = 0, limit: int = 20) -> list[Cliente]:
        return await self.repo.list_all(skip, limit)
