import pytest


async def _criar_cliente_e_conta(client, email="cliente_conta@teste.com", cpf="11122233344"):
    payload = {"nome": "Cliente Conta", "cpf": cpf, "email": email, "senha": "senha123"}
    resp = await client.post("/api/v1/clientes", json=payload)
    cliente_id = resp.json()["id"]

    resp = await client.post("/api/v1/contas", json={"cliente_id": cliente_id})
    return cliente_id, resp.json()


@pytest.mark.asyncio
async def test_criar_conta_sucesso(client):
    cliente_id, conta = await _criar_cliente_e_conta(client)
    assert conta["cliente_id"] == cliente_id
    assert conta["status"] == "ATIVA"
    assert float(conta["saldo"]) == 0.0


@pytest.mark.asyncio
async def test_criar_conta_cliente_inexistente(client):
    resp = await client.post("/api/v1/contas", json={"cliente_id": "id-invalido"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_consultar_saldo(client):
    _, conta = await _criar_cliente_e_conta(client)
    resp = await client.get(f"/api/v1/contas/{conta['id']}/saldo")
    assert resp.status_code == 200
    assert float(resp.json()["saldo"]) == 0.0


@pytest.mark.asyncio
async def test_bloquear_e_desbloquear_conta(client):
    _, conta = await _criar_cliente_e_conta(client)
    conta_id = conta["id"]

    resp = await client.patch(f"/api/v1/contas/{conta_id}/bloquear")
    assert resp.status_code == 200
    assert resp.json()["status"] == "BLOQUEADA"

    resp = await client.patch(f"/api/v1/contas/{conta_id}/desbloquear")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ATIVA"


@pytest.mark.asyncio
async def test_encerrar_conta_com_saldo_falha(client):
    _, conta = await _criar_cliente_e_conta(client)
    conta_id = conta["id"]
    await client.post("/api/v1/transacoes/deposito", json={"conta_id": conta_id, "valor": "50.00"})

    resp = await client.delete(f"/api/v1/contas/{conta_id}")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_encerrar_conta_sem_saldo_sucesso(client):
    _, conta = await _criar_cliente_e_conta(client)
    resp = await client.delete(f"/api/v1/contas/{conta['id']}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ENCERRADA"
