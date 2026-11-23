"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("cpf", sa.String(14), nullable=False, unique=True),
        sa.Column("email", sa.String(150), nullable=False, unique=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_clientes_cpf", "clientes", ["cpf"])
    op.create_index("ix_clientes_email", "clientes", ["email"])

    op.create_table(
        "contas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("numero", sa.String(20), nullable=False, unique=True),
        sa.Column("cliente_id", sa.String(36), sa.ForeignKey("clientes.id"), nullable=False),
        sa.Column("saldo", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.Enum("ATIVA", "BLOQUEADA", "ENCERRADA", name="statusconta"), nullable=False,
                   server_default="ATIVA"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_contas_numero", "contas", ["numero"])
    op.create_index("ix_contas_cliente_id", "contas", ["cliente_id"])

    op.create_table(
        "transacoes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conta_id", sa.String(36), sa.ForeignKey("contas.id"), nullable=False),
        sa.Column("conta_destino_id", sa.String(36), sa.ForeignKey("contas.id"), nullable=True),
        sa.Column("tipo", sa.Enum("DEPOSITO", "SAQUE", "TRANSFERENCIA_ENVIADA", "TRANSFERENCIA_RECEBIDA",
                                   name="tipotransacao"), nullable=False),
        sa.Column("valor", sa.Numeric(14, 2), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_transacoes_conta_id", "transacoes", ["conta_id"])
    op.create_index("ix_transacoes_conta_destino_id", "transacoes", ["conta_destino_id"])
    op.create_index("ix_transacoes_created_at", "transacoes", ["created_at"])


def downgrade() -> None:
    op.drop_table("transacoes")
    op.drop_table("contas")
    op.drop_table("clientes")
