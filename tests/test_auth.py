import pytest


@pytest.mark.asyncio
async def test_login_sucesso(client):
    payload = {"nome": "Auth Teste", "cpf": "98765432100", "email": "auth@teste.com", "senha": "minhasenha"}
    await client.post("/api/v1/clientes", json=payload)

    resp = await client.post("/api/v1/auth/login", json={"email": "auth@teste.com", "senha": "minhasenha"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_senha_invalida(client):
    payload = {"nome": "Auth Teste 2", "cpf": "98765432101", "email": "auth2@teste.com", "senha": "minhasenha"}
    await client.post("/api/v1/clientes", json=payload)

    resp = await client.post("/api/v1/auth/login", json={"email": "auth2@teste.com", "senha": "errada"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_email_inexistente(client):
    resp = await client.post("/api/v1/auth/login", json={"email": "ninguem@teste.com", "senha": "x"})
    assert resp.status_code == 401
