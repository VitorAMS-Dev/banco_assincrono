import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    contas = relationship("Conta", back_populates="cliente", cascade="all, delete-orphan")
