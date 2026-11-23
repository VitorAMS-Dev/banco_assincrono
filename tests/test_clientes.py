import pytest


@pytest.mark.asyncio
async def test_criar_cliente_sucesso(client):
    payload = {"nome": "Maria Teste", "cpf": "12345678901", "email": "maria@teste.com", "senha": "senha123"}
    resp = await client.post("/api/v1/clientes", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["nome"] == "Maria Teste"
    assert "id" in data


@pytest.mark.asyncio
async def test_criar_cliente_duplicado(client):
    payload = {"nome": "Maria Teste", "cpf": "12345678901", "email": "maria@teste.com", "senha": "senha123"}
    await client.post("/api/v1/clientes", json=payload)
    resp = await client.post("/api/v1/clientes", json=payload)
    assert resp.status_code == 409
    assert resp.json()["success"] is False


@pytest.mark.asyncio
async def test_obter_cliente_inexistente(client):
    resp = await client.get("/api/v1/clientes/id-que-nao-existe")
    assert resp.status_code == 404
