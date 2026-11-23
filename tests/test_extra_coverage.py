import pytest


async def _criar_conta(client, email, cpf, saldo_inicial="0"):
    payload = {"nome": "Cliente Extra", "cpf": cpf, "email": email, "senha": "senha123"}
    resp = await client.post("/api/v1/clientes", json=payload)
    cliente_id = resp.json()["id"]
    resp = await client.post("/api/v1/contas", json={"cliente_id": cliente_id})
    conta = resp.json()
    if float(saldo_inicial) > 0:
        await client.post("/api/v1/transacoes/deposito", json={"conta_id": conta["id"], "valor": saldo_inicial})
    return cliente_id, conta


@pytest.mark.asyncio
async def test_listar_clientes(client):
    await client.post("/api/v1/clientes", json={"nome": "Ana Lista", "cpf": "10101010101", "email": "a@a.com", "senha": "123456"})
    await client.post("/api/v1/clientes", json={"nome": "Bia Lista", "cpf": "20202020202", "email": "b@b.com", "senha": "123456"})
    resp = await client.get("/api/v1/clientes", params={"limit": 10})
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


@pytest.mark.asyncio
async def test_obter_conta_inexistente(client):
    resp = await client.get("/api/v1/contas/conta-fake")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_listar_contas_por_cliente(client):
    cliente_id, conta = await _criar_conta(client, "listc@teste.com", "30303030303")
    resp = await client.get(f"/api/v1/contas/cliente/{cliente_id}")
    assert resp.status_code == 200
    assert any(c["id"] == conta["id"] for c in resp.json())


@pytest.mark.asyncio
async def test_transferencia_conta_destino_inexistente(client):
    _, origem = await _criar_conta(client, "origemx@teste.com", "40404040404", saldo_inicial="100.00")
    resp = await client.post(
        "/api/v1/transacoes/transferencia",
        json={"conta_origem_id": origem["id"], "conta_destino_id": "fake-id", "valor": "10.00"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_transferencia_conta_destino_bloqueada(client):
    _, origem = await _criar_conta(client, "origemy@teste.com", "50505050505", saldo_inicial="100.00")
    _, destino = await _criar_conta(client, "destinoy@teste.com", "60606060606")
    await client.patch(f"/api/v1/contas/{destino['id']}/bloquear")

    resp = await client.post(
        "/api/v1/transacoes/transferencia",
        json={"conta_origem_id": origem["id"], "conta_destino_id": destino["id"], "valor": "10.00"},
    )
    assert resp.status_code == 423


@pytest.mark.asyncio
async def test_saque_conta_inexistente(client):
    resp = await client.post("/api/v1/transacoes/saque", json={"conta_id": "fake", "valor": "10.00"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_historico_alias_de_extrato(client):
    _, conta = await _criar_conta(client, "histo@teste.com", "70707070707", saldo_inicial="0")
    await client.post("/api/v1/transacoes/deposito", json={"conta_id": conta["id"], "valor": "10.00"})
    resp = await client.get(f"/api/v1/transacoes/historico/{conta['id']}")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_extrato_conta_inexistente(client):
    resp = await client.get("/api/v1/transacoes/extrato/conta-fake")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_health_e_root(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    resp = await client.get("/")
    assert resp.status_code == 200
