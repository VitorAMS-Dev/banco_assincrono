import pytest


async def _criar_conta(client, email, cpf, saldo_inicial="0"):
    payload = {"nome": "Cliente Transacao", "cpf": cpf, "email": email, "senha": "senha123"}
    resp = await client.post("/api/v1/clientes", json=payload)
    cliente_id = resp.json()["id"]
    resp = await client.post("/api/v1/contas", json={"cliente_id": cliente_id})
    conta = resp.json()
    if float(saldo_inicial) > 0:
        await client.post("/api/v1/transacoes/deposito", json={"conta_id": conta["id"], "valor": saldo_inicial})
    return conta


@pytest.mark.asyncio
async def test_deposito_sucesso(client):
    conta = await _criar_conta(client, "dep@teste.com", "22233344455")
    resp = await client.post("/api/v1/transacoes/deposito", json={"conta_id": conta["id"], "valor": "100.00"})
    assert resp.status_code == 200
    assert resp.json()["tipo"] == "DEPOSITO"

    saldo = await client.get(f"/api/v1/contas/{conta['id']}/saldo")
    assert float(saldo.json()["saldo"]) == 100.00


@pytest.mark.asyncio
async def test_saque_com_saldo_insuficiente(client):
    conta = await _criar_conta(client, "saque@teste.com", "33344455566")
    resp = await client.post("/api/v1/transacoes/saque", json={"conta_id": conta["id"], "valor": "50.00"})
    assert resp.status_code == 422
    assert resp.json()["success"] is False


@pytest.mark.asyncio
async def test_saque_sucesso(client):
    conta = await _criar_conta(client, "saque2@teste.com", "44455566677", saldo_inicial="200.00")
    resp = await client.post("/api/v1/transacoes/saque", json={"conta_id": conta["id"], "valor": "50.00"})
    assert resp.status_code == 200

    saldo = await client.get(f"/api/v1/contas/{conta['id']}/saldo")
    assert float(saldo.json()["saldo"]) == 150.00


@pytest.mark.asyncio
async def test_transferencia_sucesso(client):
    origem = await _criar_conta(client, "origem@teste.com", "55566677788", saldo_inicial="300.00")
    destino = await _criar_conta(client, "destino@teste.com", "66677788899")

    resp = await client.post(
        "/api/v1/transacoes/transferencia",
        json={"conta_origem_id": origem["id"], "conta_destino_id": destino["id"], "valor": "100.00"},
    )
    assert resp.status_code == 200

    saldo_origem = await client.get(f"/api/v1/contas/{origem['id']}/saldo")
    saldo_destino = await client.get(f"/api/v1/contas/{destino['id']}/saldo")
    assert float(saldo_origem.json()["saldo"]) == 200.00
    assert float(saldo_destino.json()["saldo"]) == 100.00


@pytest.mark.asyncio
async def test_transferencia_mesma_conta_falha(client):
    conta = await _criar_conta(client, "self@teste.com", "77788899900", saldo_inicial="100.00")
    resp = await client.post(
        "/api/v1/transacoes/transferencia",
        json={"conta_origem_id": conta["id"], "conta_destino_id": conta["id"], "valor": "10.00"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_operacao_em_conta_bloqueada_falha(client):
    conta = await _criar_conta(client, "bloq@teste.com", "88899900011", saldo_inicial="100.00")
    await client.patch(f"/api/v1/contas/{conta['id']}/bloquear")

    resp = await client.post("/api/v1/transacoes/deposito", json={"conta_id": conta["id"], "valor": "10.00"})
    assert resp.status_code == 423


@pytest.mark.asyncio
async def test_extrato_paginado(client):
    conta = await _criar_conta(client, "extrato@teste.com", "99900011122", saldo_inicial="0")
    for valor in ["10.00", "20.00", "30.00"]:
        await client.post("/api/v1/transacoes/deposito", json={"conta_id": conta["id"], "valor": valor})

    resp = await client.get(f"/api/v1/transacoes/extrato/{conta['id']}", params={"pagina": 1, "tamanho_pagina": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["transacoes"]) == 2
