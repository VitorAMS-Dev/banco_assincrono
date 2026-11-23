from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.transacao import TipoTransacao


class TransacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conta_id: str
    conta_destino_id: str | None = None
    tipo: TipoTransacao
    valor: Decimal
    descricao: str | None = None
    created_at: datetime


class ExtratoOut(BaseModel):
    conta_id: str
    saldo_atual: Decimal
    transacoes: list[TransacaoOut]
    pagina: int
    tamanho_pagina: int
    total: int
