"""
Popula o banco automaticamente com dados fictícios via Faker, de forma assíncrona.
Cria 20 clientes, 20 contas e 100 transações por padrão (configurável via .env).
Idempotente: só executa se a tabela de clientes estiver vazia.
"""
import random
from decimal import Decimal

from faker import Faker
from sqlalchemy import select, func

from app.core.config import settings
from app.core.logging_config import database_logger
from app.core.security import hash_password
from app.database.session import AsyncSessionLocal
from app.models.cliente import Cliente
from app.models.conta import Conta, StatusConta
from app.models.transacao import Transacao, TipoTransacao

fake = Faker("pt_BR")


def _gerar_numero_conta(usados: set[str]) -> str:
    numero = f"{random.randint(1000, 9999)}-{random.randint(0, 9)}"
    while numero in usados:
        numero = f"{random.randint(1000, 9999)}-{random.randint(0, 9)}"
    usados.add(numero)
    return numero


async def seed_database() -> None:
    async with AsyncSessionLocal() as session:
        total_clientes = await session.execute(select(func.count()).select_from(Cliente))
        if total_clientes.scalar_one() > 0:
            database_logger.info("Seed ignorado: banco já populado.")
            return

        database_logger.info("Iniciando seed do banco de dados...")
        senha_hash_padrao = await hash_password("senha123")

        clientes = []
        for _ in range(settings.SEED_CLIENTES):
            cliente = Cliente(
                nome=fake.unique.name(),
                cpf=fake.unique.cpf(),
                email=fake.unique.email(),
                senha_hash=senha_hash_padrao,
            )
            session.add(cliente)
            clientes.append(cliente)
        await session.commit()

        numeros_usados: set[str] = set()
        contas = []
        for cliente in clientes[: settings.SEED_CONTAS]:
            conta = Conta(
                numero=_gerar_numero_conta(numeros_usados),
                cliente_id=cliente.id,
                saldo=Decimal(random.randint(100, 10000)),
                status=StatusConta.ATIVA,
            )
            session.add(conta)
            contas.append(conta)
        await session.commit()

        for _ in range(settings.SEED_TRANSACOES):
            conta = random.choice(contas)
            tipo = random.choice([TipoTransacao.DEPOSITO, TipoTransacao.SAQUE])
            valor = Decimal(random.randint(10, 500))
            session.add(Transacao(conta_id=conta.id, tipo=tipo, valor=valor, descricao=fake.sentence(nb_words=6)))
        await session.commit()

        database_logger.info(
            "Seed concluído: %s clientes, %s contas, %s transações.",
            len(clientes), len(contas), settings.SEED_TRANSACOES,
        )
