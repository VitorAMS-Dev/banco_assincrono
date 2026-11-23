from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.conta import StatusConta


class ContaCreate(BaseModel):
    cliente_id: str


class ContaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    numero: str
    cliente_id: str
    saldo: Decimal
    status: StatusConta
    created_at: datetime


class SaldoOut(BaseModel):
    conta_id: str
    saldo: Decimal


class DepositoRequest(BaseModel):
    conta_id: str
    valor: Decimal = Field(gt=0)


class SaqueRequest(BaseModel):
    conta_id: str
    valor: Decimal = Field(gt=0)


class TransferenciaRequest(BaseModel):
    conta_origem_id: str
    conta_destino_id: str
    valor: Decimal = Field(gt=0)
