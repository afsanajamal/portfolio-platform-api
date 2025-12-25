# Development Guide

Quick reference for common development tasks.

---

## Setup

### First Time Setup

```bash
# Clone repository
git clone https://github.com/afsanajamal/portfolio-platform-api.git
cd portfolio-platform-api

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL with Docker
docker-compose up -d

# Run database migrations
alembic upgrade head

# Seed test data
PYTHONPATH=. python scripts/seed_admin.py

# Start development server
uvicorn app.main:app --reload
```

### Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql+psycopg://portfolio:portfolio@localhost:5432/portfolio_db

# JWT
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## Common Tasks

### Start Development Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Start with auto-reload
uvicorn app.main:app --reload

# Or with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Opens at http://127.0.0.1:8000

API docs at http://127.0.0.1:8000/docs

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_auth.py

# Specific test function
pytest tests/test_auth.py::test_register_user

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# See migration history
alembic history

# Reset database (WARNING: Deletes all data)
alembic downgrade base
alembic upgrade head
```

### Seed Data

```bash
# Seed admin and test users
PYTHONPATH=. python scripts/seed_admin.py
```

Creates:
- Organization: "Demo Org"
- Users:
  - admin@example.com / admin12345 (Admin)
  - editor@example.com / editor12345 (Editor)
  - viewer@example.com / viewer12345 (Viewer)

---

## Adding New Features

### Adding a New Endpoint

1. **Create Pydantic schemas** in `app/schemas/`

```python
# app/schemas/feature.py
from pydantic import BaseModel

class FeatureCreate(BaseModel):
    name: str
    description: str

class FeatureResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True
```

2. **Create database model** in `app/models/`

```python
# app/models/feature.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base_class import Base

class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
```

3. **Create migration**

```bash
alembic revision --autogenerate -m "add feature table"
alembic upgrade head
```

4. **Create route** in `app/api/routes/`

```python
# app/api/routes/features.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_admin
from app.schemas.feature import FeatureCreate, FeatureResponse
from app.models.feature import Feature

router = APIRouter()

@router.post("/", response_model=FeatureResponse)
def create_feature(
    feature: FeatureCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_admin)
):
    db_feature = Feature(**feature.dict(), org_id=current_user.org_id)
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature
```

5. **Register route** in `app/api/router.py`

```python
from app.api.routes import features

api_router.include_router(features.router, prefix="/features", tags=["features"])
```

6. **Write tests** in `tests/`

```python
# tests/test_features.py
def test_create_feature(client, admin_token_headers):
    response = client.post(
        "/features",
        json={"name": "Test Feature", "description": "Test"},
        headers=admin_token_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Feature"
```

---

## Testing

### Writing Tests

Create `tests/test_your_feature.py`:

```python
import pytest
from fastapi.testclient import TestClient

def test_your_endpoint(client: TestClient, admin_token_headers):
    response = client.get("/your-endpoint", headers=admin_token_headers)
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

### Test Fixtures

Use existing fixtures from `tests/conftest.py`:

- `client` - FastAPI test client
- `db` - Test database session
- `admin_token_headers` - Admin auth headers
- `editor_token_headers` - Editor auth headers
- `viewer_token_headers` - Viewer auth headers

### Test Database

Tests use SQLite in memory:
- Fast execution
- No cleanup needed
- Fresh database per test session

---

## Authentication

### Dependencies

```python
from app.api.deps import (
    get_current_user,        # Any authenticated user
    get_current_user_admin,  # Admin only
    require_admin_or_editor  # Admin or Editor
)

@router.post("/endpoint")
def endpoint(current_user = Depends(get_current_user)):
    # current_user is automatically injected
    return {"user_id": current_user.id}
```

### Creating Tokens

```python
from app.core.security import create_access_token, create_refresh_token

access_token = create_access_token(
    subject=user.email,
    org_id=user.org_id,
    role=user.role,
    user_id=user.id
)

refresh_token = create_refresh_token(subject=user.email)
```

### Verifying Passwords

```python
from app.core.security import verify_password, hash_password

# Hash password
hashed = hash_password("plain_password")

# Verify password
is_valid = verify_password("plain_password", hashed)
```

---

## RBAC Patterns

### Endpoint Protection

```python
from app.api.deps import get_current_user_admin

@router.get("/admin-only")
def admin_endpoint(current_user = Depends(get_current_user_admin)):
    # Only admins can access this
    return {"message": "Admin access granted"}
```

### Custom Permission Checks

```python
from fastapi import HTTPException, status

def check_project_ownership(project_id: int, user, db: Session):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Admin can access any project
    if user.role == "admin":
        return project

    # Others can only access their own
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return project
```

---

## Database Queries

### Basic CRUD

```python
from sqlalchemy.orm import Session
from app.models.project import Project

# Create
project = Project(title="New Project", org_id=1)
db.add(project)
db.commit()
db.refresh(project)

# Read
project = db.query(Project).filter(Project.id == 1).first()
projects = db.query(Project).filter(Project.org_id == 1).all()

# Update
project.title = "Updated Title"
db.commit()

# Delete
db.delete(project)
db.commit()
```

### Filtering and Joins

```python
from sqlalchemy import and_, or_

# Multiple filters
projects = db.query(Project).filter(
    and_(
        Project.org_id == user.org_id,
        Project.is_public == True
    )
).all()

# Ordering
projects = db.query(Project).order_by(Project.created_at.desc()).all()

# Limit and offset
projects = db.query(Project).limit(10).offset(20).all()
```

---

## Logging Activity

```python
from app.models.activity_log import ActivityLog

def log_activity(db: Session, action: str, entity: str, entity_id: int, user_id: int):
    log = ActivityLog(
        action=action,
        entity=entity,
        entity_id=entity_id,
        actor_user_id=user_id
    )
    db.add(log)
    db.commit()

# Usage
log_activity(db, "CREATE", "project", project.id, current_user.id)
```

---

## Debugging

### Python Debugger (pdb)

```python
import pdb; pdb.set_trace()  # Set breakpoint

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

### Print Database Queries

```python
# Add to app/db/session.py
engine = create_engine(
    DATABASE_URL,
    echo=True  # Print all SQL queries
)
```

### FastAPI Debug Mode

```python
# app/main.py
app = FastAPI(debug=True)
```

---

## Common Issues

### "relation does not exist" error
- Run migrations: `alembic upgrade head`
- Check database connection in `.env`

### Import errors
- Set `PYTHONPATH=.` before running scripts
- Or use: `python -m pytest` instead of `pytest`

### Migration conflicts
```bash
# Rollback and reapply
alembic downgrade -1
alembic upgrade head

# Or reset (WARNING: deletes data)
alembic downgrade base
alembic upgrade head
```

### Test database locked
- Tests use in-memory SQLite, shouldn't lock
- If using PostgreSQL for tests, ensure test DB is separate

### "Secret key not set" error
- Create `.env` file with `SECRET_KEY`
- Or set environment variable: `export SECRET_KEY="your-key"`

---

## Code Style

### Python
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Use docstrings for public functions
- Prefer explicit over implicit

### Naming
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Imports
Order imports:
1. Standard library
2. Third-party libraries
3. Local application imports

```python
import os
from datetime import datetime

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password
```

---

## API Documentation

FastAPI automatically generates:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

### Improving Documentation

```python
@router.post(
    "/",
    response_model=ProjectResponse,
    summary="Create a new project",
    description="Creates a new project in the current user's organization",
    responses={
        200: {"description": "Project created successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Not authenticated"}
    }
)
def create_project(...):
    pass
```

---

## Performance Tips

### Database Queries
- Use `select_in_load` for eager loading relationships
- Add indexes to frequently queried columns
- Use pagination for large result sets

### Caching
- Consider caching frequently accessed data
- Use Redis for distributed caching (future enhancement)

### Background Tasks
```python
from fastapi import BackgroundTasks

@router.post("/send-email")
def send_email(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_task, "user@example.com")
    return {"message": "Email will be sent"}
```

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: add your feature"

# Push to GitHub
git push origin feature/your-feature

# Create pull request on GitHub
```

### Commit Message Format

Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Add/update tests
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `chore:` - Build/config changes

---

## Production Deployment

### Environment Variables

Set in production:
```env
DATABASE_URL=postgresql://...
SECRET_KEY=strong-random-key-here
ENVIRONMENT=production
```

### Run with Gunicorn

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Database Migrations

```bash
# Apply migrations
alembic upgrade head

# Never use --autogenerate in production
# Always review migration files before applying
```

---

## Useful Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# Create requirements.txt
pip freeze > requirements.txt

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Deactivate virtual environment
deactivate

# Run specific test with output
pytest tests/test_auth.py -v -s

# Format code with black
black app/ tests/

# Lint with flake8
flake8 app/ tests/
```

---

## Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [Pytest Documentation](https://docs.pytest.org)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
