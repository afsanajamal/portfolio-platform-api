# Project & Portfolio Platform API (FastAPI + PostgreSQL)

A backend-first, multi-tenant API meant to make a **good impression on backend engineers**:
- Organizations (multi-tenant)
- JWT auth (access + refresh)
- RBAC: admin / editor / viewer
- Projects (public/private) + tags (many-to-many)
- Activity/Audit log on mutations
- Alembic migrations
- Pytest API tests
- Docker Compose for PostgreSQL

## Run locally

### 1) Start Postgres
```bash
docker compose up -d
```

### 2) Setup python env
```bash
python -m venv .venv
# mac/linux:
source .venv/bin/activate
# windows (powershell):
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3) Configure env
```bash
cp .env.example .env
# set JWT_SECRET to something long/random
```

### 4) Migrate DB
```bash
alembic upgrade head
```

### 5) Seed demo admin (optional)
```bash
python scripts/seed_admin.py
```

### 6) Run API
```bash
uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

## Testing (uses SQLite test DB)
```bash
pytest -q
```

## Roles
- admin: manage users + view activity + full CRUD
- editor: create/update projects + create tags
- viewer: read-only

