"""
Camada visual da aplicação bancária.
Flask serve apenas HTML/CSS/JS e consome a API FastAPI assíncrona via HTTP.
Toda regra de negócio (saldo, transferência, etc.) vive exclusivamente na API.
"""
import os
from decimal import Decimal, InvalidOperation

import requests
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "troque_esta_chave_flask")

API_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 10


def api_get(path, **kwargs):
    return requests.get(f"{API_BASE_URL}{path}", timeout=REQUEST_TIMEOUT, **kwargs)


def api_post(path, **kwargs):
    return requests.post(f"{API_BASE_URL}{path}", timeout=REQUEST_TIMEOUT, **kwargs)


def api_patch(path, **kwargs):
    return requests.patch(f"{API_BASE_URL}{path}", timeout=REQUEST_TIMEOUT, **kwargs)


def extrair_erro(resp):
    try:
        return resp.json().get("message", "Erro inesperado.")
    except Exception:
        return "Erro inesperado ao comunicar com a API."


def login_obrigatorio():
    return "cliente_id" not in session


@app.context_processor
def inject_session():
    return {
        "logado": not login_obrigatorio(),
        "nome_cliente": session.get("nome_cliente"),
    }


@app.route("/")
def index():
    if login_obrigatorio():
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        resp = api_post("/api/v1/auth/login", json={"email": email, "senha": senha})
        if resp.status_code != 200:
            flash(extrair_erro(resp), "erro")
            return render_template("login.html")

        token = resp.json()["access_token"]
        session["token"] = token

        # localizar cliente pelo e-mail para obter id/nome/contas (camada visual apenas)
        clientes_resp = api_get("/api/v1/clientes", params={"limit": 200})
        cliente = next((c for c in clientes_resp.json() if c["email"] == email), None)
        if not cliente:
            flash("Cliente autenticado, porém não localizado para exibição.", "erro")
            return render_template("login.html")

        session["cliente_id"] = cliente["id"]
        session["nome_cliente"] = cliente["nome"]
        flash(f"Bem-vindo(a), {cliente['nome']}.", "sucesso")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if login_obrigatorio():
        return redirect(url_for("login"))

    cliente_id = session["cliente_id"]
    contas_resp = api_get(f"/api/v1/contas/cliente/{cliente_id}")
    contas = contas_resp.json() if contas_resp.status_code == 200 else []

    conta_id = request.args.get("conta_id") or (contas[0]["id"] if contas else None)
    conta_atual = next((c for c in contas if c["id"] == conta_id), None)

    return render_template("dashboard.html", contas=contas, conta_atual=conta_atual)


@app.route("/conta/<conta_id>/nova", methods=["POST"])
def criar_conta(conta_id=None):
    if login_obrigatorio():
        return redirect(url_for("login"))
    resp = api_post("/api/v1/contas", json={"cliente_id": session["cliente_id"]})
    if resp.status_code == 201:
        flash("Nova conta criada com sucesso.", "sucesso")
    else:
        flash(extrair_erro(resp), "erro")
    return redirect(url_for("dashboard"))


def _parse_valor(valor_str):
    try:
        valor = Decimal(valor_str.replace(",", "."))
        if valor <= 0:
            return None
        return valor
    except (InvalidOperation, AttributeError):
        return None


@app.route("/transacao/deposito", methods=["POST"])
def deposito():
    if login_obrigatorio():
        return redirect(url_for("login"))

    conta_id = request.form.get("conta_id")
    valor = _parse_valor(request.form.get("valor", ""))
    if not valor:
        flash("Informe um valor válido para o depósito.", "erro")
        return redirect(url_for("dashboard", conta_id=conta_id))

    resp = api_post("/api/v1/transacoes/deposito", json={"conta_id": conta_id, "valor": str(valor)})
    if resp.status_code == 200:
        flash(f"Depósito de R$ {valor:.2f} realizado com sucesso.", "sucesso")
    else:
        flash(extrair_erro(resp), "erro")
    return redirect(url_for("dashboard", conta_id=conta_id))


@app.route("/transacao/saque", methods=["POST"])
def saque():
    if login_obrigatorio():
        return redirect(url_for("login"))

    conta_id = request.form.get("conta_id")
    valor = _parse_valor(request.form.get("valor", ""))
    if not valor:
        flash("Informe um valor válido para o saque.", "erro")
        return redirect(url_for("dashboard", conta_id=conta_id))

    resp = api_post("/api/v1/transacoes/saque", json={"conta_id": conta_id, "valor": str(valor)})
    if resp.status_code == 200:
        flash(f"Saque de R$ {valor:.2f} realizado com sucesso.", "sucesso")
    else:
        flash(extrair_erro(resp), "erro")
    return redirect(url_for("dashboard", conta_id=conta_id))


@app.route("/transacao/transferencia", methods=["POST"])
def transferencia():
    if login_obrigatorio():
        return redirect(url_for("login"))

    conta_origem_id = request.form.get("conta_id")
    conta_destino_numero = request.form.get("conta_destino", "").strip()
    valor = _parse_valor(request.form.get("valor", ""))

    if not valor:
        flash("Informe um valor válido para a transferência.", "erro")
        return redirect(url_for("dashboard", conta_id=conta_origem_id))

    # Resolve número da conta destino -> id (camada visual apenas; lógica real está na API)
    contas_resp = api_get(f"/api/v1/contas/cliente/{session['cliente_id']}")
    todas_contas = contas_resp.json() if contas_resp.status_code == 200 else []
    conta_destino = next((c for c in todas_contas if c["numero"] == conta_destino_numero), None)

    if not conta_destino:
        flash("Conta de destino não encontrada entre suas contas. Informe um número válido.", "erro")
        return redirect(url_for("dashboard", conta_id=conta_origem_id))

    resp = api_post(
        "/api/v1/transacoes/transferencia",
        json={
            "conta_origem_id": conta_origem_id,
            "conta_destino_id": conta_destino["id"],
            "valor": str(valor),
        },
    )
    if resp.status_code == 200:
        flash(f"Transferência de R$ {valor:.2f} realizada com sucesso.", "sucesso")
    else:
        flash(extrair_erro(resp), "erro")
    return redirect(url_for("dashboard", conta_id=conta_origem_id))


@app.route("/conta/<conta_id>/bloquear", methods=["POST"])
def bloquear(conta_id):
    if login_obrigatorio():
        return redirect(url_for("login"))
    resp = api_patch(f"/api/v1/contas/{conta_id}/bloquear")
    flash("Conta bloqueada." if resp.status_code == 200 else extrair_erro(resp),
          "sucesso" if resp.status_code == 200 else "erro")
    return redirect(url_for("dashboard", conta_id=conta_id))


@app.route("/conta/<conta_id>/desbloquear", methods=["POST"])
def desbloquear(conta_id):
    if login_obrigatorio():
        return redirect(url_for("login"))
    resp = api_patch(f"/api/v1/contas/{conta_id}/desbloquear")
    flash("Conta desbloqueada." if resp.status_code == 200 else extrair_erro(resp),
          "sucesso" if resp.status_code == 200 else "erro")
    return redirect(url_for("dashboard", conta_id=conta_id))


@app.route("/extrato/<conta_id>")
def extrato(conta_id):
    if login_obrigatorio():
        return redirect(url_for("login"))

    pagina = int(request.args.get("pagina", 1))
    resp = api_get(f"/api/v1/transacoes/extrato/{conta_id}", params={"pagina": pagina, "tamanho_pagina": 10})
    extrato_data = resp.json() if resp.status_code == 200 else None
    if not extrato_data:
        flash(extrair_erro(resp), "erro")
        return redirect(url_for("dashboard"))

    return render_template("extrato.html", extrato=extrato_data, conta_id=conta_id, pagina=pagina)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
