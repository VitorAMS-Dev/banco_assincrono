import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class StatusConta(str, enum.Enum):
    ATIVA = "ATIVA"
    BLOQUEADA = "BLOQUEADA"
    ENCERRADA = "ENCERRADA"


class Conta(Base):
    __tablename__ = "contas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    cliente_id: Mapped[str] = mapped_column(String(36), ForeignKey("clientes.id"), nullable=False, index=True)
    saldo: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    status: Mapped[StatusConta] = mapped_column(Enum(StatusConta), nullable=False, default=StatusConta.ATIVA)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cliente = relationship("Cliente", back_populates="contas")
    transacoes = relationship(
        "Transacao",
        back_populates="conta",
        cascade="all, delete-orphan",
        foreign_keys="Transacao.conta_id",
    )
