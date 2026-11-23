import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class TipoTransacao(str, enum.Enum):
    DEPOSITO = "DEPOSITO"
    SAQUE = "SAQUE"
    TRANSFERENCIA_ENVIADA = "TRANSFERENCIA_ENVIADA"
    TRANSFERENCIA_RECEBIDA = "TRANSFERENCIA_RECEBIDA"


class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conta_id: Mapped[str] = mapped_column(String(36), ForeignKey("contas.id"), nullable=False, index=True)
    conta_destino_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("contas.id"), nullable=True, index=True)
    tipo: Mapped[TipoTransacao] = mapped_column(Enum(TipoTransacao), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    conta = relationship("Conta", back_populates="transacoes", foreign_keys=[conta_id])
