from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ClienteCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    cpf: str = Field(min_length=11, max_length=14)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=128)


class ClienteLogin(BaseModel):
    email: EmailStr
    senha: str


class ClienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    cpf: str
    email: EmailStr
    created_at: datetime
