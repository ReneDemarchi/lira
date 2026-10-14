# LIRA — Gerenciador Ágil de Projetos

Gerenciador de projetos estilo Jira, mais simples: projetos, tarefas, board com arrastar e soltar,
etiquetas, comentários e papéis por projeto (Administrador, Coordenador, Colaborador).

Feito com Django 5.2 + PostgreSQL 17 + Bootstrap.

## Pré-requisitos

- Python 3.12+
- Docker (com Docker Compose)

## Rodando

```sh
git clone git@github.com:ReneDemarchi/lira.git
cd lira

docker compose up -d                          # sobe o Postgres na porta 5433
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Abra http://localhost:8000, crie uma conta em **Cadastro** e pronto.

Não precisa de `.env`: os valores padrão já batem com o `docker-compose.yml`.
Para mudar algo (porta, senha), copie `.env.example` para `.env` e exporte as variáveis antes do `runserver`.

> No Windows, troque `.venv/bin/` por `.venv\Scripts\`.

## Extras

```sh
.venv/bin/python manage.py createsuperuser    # acesso ao painel /admin
.venv/bin/python manage.py test core          # roda os testes
docker compose down                           # para o banco (os dados ficam salvos)
```

## Documentação

- [CONTEXT.md](CONTEXT.md) — vocabulário do domínio (Projeto, Tarefa, Papel...)
- [PLANO.md](PLANO.md) — plano de implementação e regras de negócio
- [docs/](docs/) — diagramas e entregas
