# Banco Async API

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

API bancária assíncrona desenvolvida como projeto de portfólio. O sistema simula operações essenciais de um banco digital, com cadastro de clientes e contas, autenticação JWT, depósito, saque, transferência, extrato e bloqueio ou encerramento de contas.

A aplicação separa o backend da API da interface visual: a API é feita com FastAPI e a interface web com Flask. Toda comunicação entre as duas camadas usa HTTP.

---

## Visão geral

- API `async` para rotas, serviços e acesso ao banco
- SQLAlchemy 2.0 com `AsyncSession`, PostgreSQL e asyncpg
- Cache opcional com Redis
- Autenticação com JWT HS256
- Validação de entrada e saída com Pydantic
- Seed automático e configurável para dados de demonstração
- Interface web em Flask
- Logs, IDs de requisição e timeout para operações financeiras
- Testes assíncronos com SQLite em memória
- Execução completa com Docker Compose

## Arquitetura

O projeto segue uma organização inspirada em Clean Architecture:

```text
Cliente HTTP
  |
  v
Middleware (tempo e X-Request-ID)
  |
  v
Rotas FastAPI
  |
  v
Services (regras de negócio e timeout)
  |
  +--> Repositories --> SQLAlchemy Async --> PostgreSQL
  |
  +--> CacheService --> Redis
```

| Camada | Responsabilidade |
|---|---|
| `app/api` | Endpoints FastAPI e orquestração das requisições |
| `app/services` | Regras de negócio, validações e operações financeiras |
| `app/repositories` | Consultas e persistência com `AsyncSession` |
| `app/models` | Entidades SQLAlchemy |
| `app/schemas` | Contratos Pydantic de entrada e saída |
| `app/middlewares` | Medição de tempo e ID da requisição |
| `app/exceptions` | Exceções de domínio e respostas de erro globais |
| `app/core` | Configurações, segurança JWT e logging |
| `app/database` | Engine, sessões e seed |
| `app/utils` | Notificações externas assíncronas |
| `web` | Interface Flask que consome a API |

Todas as operações críticas são executadas com `async/await`. O cache Redis é uma otimização: a indisponibilidade dele não impede o funcionamento da API.

---

## Tecnologias

**Backend**

- Python 3.12+
- FastAPI e Uvicorn
- SQLAlchemy 2.0 Async
- asyncpg
- PostgreSQL 16
- Redis 7
- Pydantic 2
- JWT via python-jose
- bcrypt
- Alembic
- httpx

**Interface**

- Flask
- HTML, CSS e JavaScript
- Requests para comunicação com a API

**Qualidade e infraestrutura**

- pytest e pytest-asyncio
- pytest-cov
- SQLite assíncrono via aiosqlite nos testes
- Docker e Docker Compose

---

## Estrutura do projeto

```text
banco_assincrono/
├── app/
│   ├── api/             # Endpoints HTTP
│   ├── core/            # Configuração, segurança e logs
│   ├── database/        # Engine, sessões e seed
│   ├── exceptions/      # Erros de domínio e handlers
│   ├── middlewares/     # Request ID e tempo de resposta
│   ├── models/          # Entidades SQLAlchemy
│   ├── repositories/    # Acesso a dados
│   ├── schemas/         # Schemas Pydantic
│   ├── services/        # Regras de negócio
│   └── utils/           # Notificador webhook
├── web/
│   ├── static/css/      # Estilos da interface
│   ├── templates/       # Páginas Flask
│   └── app.py           # Aplicação web
├── tests/               # Suíte assíncrona
├── alembic/             # Migrações do banco
├── docker/              # Dockerfiles da API e da interface
├── logs/                # Arquivos de log
├── .env.example         # Variáveis de ambiente
├── docker-compose.yml
├── main.py              # Aplicação FastAPI
└── requirements.txt
```

---

## Executando com Docker

### Pré-requisitos

- Docker Desktop
- Docker Compose

Na raiz do projeto:

```bash
cp .env.example .env
docker compose up --build
```

No PowerShell do Windows, o comando `cp` pode ser usado como alias de `Copy-Item`. Caso prefira:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Para iniciar os containers em segundo plano:

```bash
docker compose up --build -d
```

Para parar e remover os containers:

```bash
docker compose down
```

Para remover também os dados persistentes do PostgreSQL:

```bash
docker compose down -v
```

### Serviços disponíveis

| Serviço | Endereço |
|---|---|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Interface web | http://localhost:5000 |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

A API cria as tabelas no startup e executa o seed enquanto `SEED_ON_STARTUP=true`.

---

## Executando localmente

### 1. Crie o ambiente virtual

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instale as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure o ambiente

```bash
cp .env.example .env
```

Para uma execução local sem Docker, ajuste no `.env` a conexão do PostgreSQL:

```dotenv
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/banco
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=uma_chave_longa_e_secreta
```

### 4. Inicie a API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Inicie a interface web

Em outro terminal:

```bash
cd web
pip install -r requirements.txt
```

Linux/macOS:

```bash
FASTAPI_BASE_URL=http://localhost:8000 python app.py
```

Windows PowerShell:

```powershell
$env:FASTAPI_BASE_URL="http://localhost:8000"
python app.py
```

---

## Dados de demonstração

O seed roda automaticamente no startup quando `SEED_ON_STARTUP=true`. Por padrão, ele cria:

- 20 clientes
- 20 contas
- 100 transações

Os valores podem ser alterados pelas variáveis `SEED_CLIENTES`, `SEED_CONTAS` e `SEED_TRANSACOES`.

O seed é idempotente: ele não insere novos dados quando a tabela de clientes já contém registros.

Todos os clientes criados pelo seed usam:

```text
Senha: senha123
```

Os e-mails são gerados aleatoriamente. Em ambiente Docker, eles podem ser obtidos no banco ou pela resposta de `GET /api/v1/clientes`.

Para desativar o seed:

```dotenv
SEED_ON_STARTUP=false
```

---

## Endpoints principais

| Metodo | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Verificação de saúde da aplicação |
| `POST` | `/api/v1/auth/login` | Login e emissão do JWT |
| `POST` | `/api/v1/clientes` | Cadastro de cliente |
| `GET` | `/api/v1/clientes` | Lista clientes |
| `GET` | `/api/v1/clientes/{cliente_id}` | Busca cliente por ID |
| `POST` | `/api/v1/contas` | Cria conta para um cliente |
| `GET` | `/api/v1/contas/{conta_id}` | Busca conta por ID |
| `GET` | `/api/v1/contas/{conta_id}/saldo` | Consulta saldo |
| `GET` | `/api/v1/contas/cliente/{cliente_id}` | Lista contas de um cliente |
| `PATCH` | `/api/v1/contas/{conta_id}/bloquear` | Bloqueia conta |
| `PATCH` | `/api/v1/contas/{conta_id}/desbloquear` | Desbloqueia conta |
| `DELETE` | `/api/v1/contas/{conta_id}` | Encerra conta |
| `POST` | `/api/v1/transacoes/deposito` | Realiza depósito |
| `POST` | `/api/v1/transacoes/saque` | Realiza saque |
| `POST` | `/api/v1/transacoes/transferencia` | Realiza transferência |
| `GET` | `/api/v1/transacoes/extrato/{conta_id}` | Consulta extrato paginado |
| `GET` | `/api/v1/transacoes/historico/{conta_id}` | Alias do extrato |

A documentação interativa em `/docs` contém os schemas, parâmetros e modelos de resposta de cada endpoint.

---

## Exemplos com cURL

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"email-gerado@example.com","senha":"senha123"}'
```

Resposta:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in_minutes": 60
}
```

### Cadastrar cliente

```bash
curl -X POST http://localhost:8000/api/v1/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Silva",
    "cpf": "12345678901",
    "email": "maria@example.com",
    "senha": "senha123"
  }'
```

### Criar conta

```bash
curl -X POST http://localhost:8000/api/v1/contas \
  -H "Content-Type: application/json" \
  -d '{"cliente_id":"<cliente_id>"}'
```

### Depositar

```bash
curl -X POST http://localhost:8000/api/v1/transacoes/deposito \
  -H "Content-Type: application/json" \
  -d '{"conta_id":"<conta_id>","valor":"150.50"}'
```

### Sacar

```bash
curl -X POST http://localhost:8000/api/v1/transacoes/saque \
  -H "Content-Type: application/json" \
  -d '{"conta_id":"<conta_id>","valor":"50.25"}'
```

### Transferir

```bash
curl -X POST http://localhost:8000/api/v1/transacoes/transferencia \
  -H "Content-Type: application/json" \
  -d '{
    "conta_origem_id":"<conta_origem_id>",
    "conta_destino_id":"<conta_destino_id>",
    "valor":"100.00"
  }'
```

### Consultar extrato

```bash
curl "http://localhost:8000/api/v1/transacoes/extrato/<conta_id>?pagina=1&tamanho_pagina=10"
```

---

## Modelo de dados

```text
Cliente 1 ───────∞ Conta 1 ───────∞ Transação
```

| Entidade | Campos principais |
|---|---|
| `Cliente` | ID, nome, CPF, e-mail, hash da senha e data de criação |
| `Conta` | ID, número, cliente, saldo, status e data de criação |
| `Transação` | ID, conta, conta de destino, tipo, valor, descrição e data |

Status da conta:

- `ATIVA`
- `BLOQUEADA`
- `ENCERRADA`

Tipos de transação:

- `DEPOSITO`
- `SAQUE`
- `TRANSFERENCIA_ENVIADA`
- `TRANSFERENCIA_RECEBIDA`

Uma transferência gera duas transações: uma saída na conta de origem e uma entrada na conta de destino.

---

## Autenticação JWT

O login em `/api/v1/auth/login` valida as credenciais e gera um token JWT HS256. A validade padrão é de 60 minutos e pode ser configurada com `JWT_EXPIRE_MINUTES`.

```dotenv
JWT_SECRET_KEY=troque_para_uma_chave_segura
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

**Importante:** neste estado do projeto, o token é emitido e pode ser validado pela infraestrutura existente, mas nenhuma rota exige `Authorization: Bearer <token>`. Os endpoints continuam públicos. Antes de uso real, proteja os endpoints sensíveis e valide se o cliente autenticado é dono da conta acessada.

---

## Testes

Instale as dependências de desenvolvimento e execute:

```bash
pytest -q
```

Para visualizar a cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```

A suíte usa uma base SQLite assíncrona em memória e `httpx.AsyncClient` contra o aplicativo ASGI. O Redis externo não é necessário para os testes, pois o cache falha de forma não bloqueante quando indisponível.

---

## Logs e observabilidade

Os logs são gravados no diretório configurado por `LOG_DIR` e têm rotação automática em até 5 MB por arquivo.

| Arquivo | Conteúdo |
|---|---|
| `app.log` | Eventos gerais e operações da aplicação |
| `error.log` | Exceções tratadas pela API |
| `access.log` | Método, caminho, status, duração e request ID |
| `database.log` | Eventos do banco e do seed |

O middleware de tempo adiciona o header `X-Request-ID` às respostas e registra o tempo de processamento das requisições.

---

## Timeouts e erros

Operações financeiras são protegidas por timeout configurável:

```python
await asyncio.wait_for(operacao(), timeout=settings.OPERATION_TIMEOUT_SECONDS)
```

O padrão é 30 segundos.

Timeout:

```json
{
  "success": false,
  "message": "Operação cancelada por tempo excedido."
}
```

Erros tratados pelo handler global seguem o formato:

```json
{
  "success": false,
  "message": "Descrição do erro."
}
```

---

## Migrações

O projeto inclui migrações Alembic. Para gerar uma nova migração após alterar os models:

```bash
alembic revision --autogenerate -m "descricao_da_migracao"
alembic upgrade head
```

---

## Variáveis de ambiente

Consulte todas as opções disponíveis em `.env.example`.

| Variável | Padrão | Uso |
|---|---|---|
| `DATABASE_URL` | PostgreSQL via asyncpg | Conexão assíncrona com o banco |
| `DATABASE_ECHO` | `false` | Exibe SQL gerado |
| `REDIS_URL` | `redis://redis:6379/0` | Conexão com Redis |
| `CACHE_TTL_SECONDS` | `30` | Tempo de cache |
| `JWT_SECRET_KEY` | — | Chave de assinatura JWT |
| `JWT_EXPIRE_MINUTES` | `60` | Expiração do token |
| `OPERATION_TIMEOUT_SECONDS` | `30` | Timeout das operações |
| `SEED_ON_STARTUP` | `true` | Executa o seed no startup |
| `NOTIFICATION_WEBHOOK_URL` | vazio | Webhook opcional de notificações |
| `FASTAPI_BASE_URL` | `http://api:8000` | URL usada pela interface Flask |

---

## Limitações conhecidas

- As operações financeiras ainda não possuem lock pessimista ou controle otimista de concorrência.
- Os endpoints não exigem autenticação JWT neste estado do projeto.
- O seed gera transações aleatórias, sem representar um histórico bancário completo.
- O webhook é opcional e falhas externas não interrompem a resposta da operação.
- O projeto é destinado a estudos e demonstrações; não deve ser usado em produção sem reforçar segurança, autorização, concorrência e observabilidade.

---

## Contribuição

1. Crie uma branch a partir da `main`.
2. Mantenha a separação entre rota, service, repository e model.
3. Use `async/await` em operações de I/O.
4. Adicione ou ajuste testes para novas regras e endpoints.
5. Execute `pytest -q` antes de abrir um pull request.

```bash
git checkout -b feature/minha-feature
# altere o projeto
pytest -q
git add .
git commit -m "Adiciona minha feature"
git push origin feature/minha-feature
```

---

## Licença

Distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE).
