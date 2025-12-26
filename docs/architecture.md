# Architecture & Design Decisions

## Framework Choice

**FastAPI** was chosen because:
- High performance (ASGI-based)
- Strong typing with Pydantic
- Built-in OpenAPI documentation
- Excellent dependency injection system

---

## Application Structure

The application follows a **modular structure**:

- `app/main.py`  
  Creates the FastAPI app using an **app factory pattern**.

- `app/api/router.py`  
  Registers all route modules.

- `app/api/routes/`  
  Feature-based routing (auth, users, projects, etc).

- `app/core/`  
  Configuration and security utilities.

- `app/db/`  
  Database engine and session management.

- `app/models/`  
  SQLAlchemy ORM models.

- `app/schemas/`  
  Pydantic request/response models.

---

## App Factory Pattern

The app is created using a factory function:

```python
def create_app() -> FastAPI:
    app = FastAPI(
        title="Portfolio Platform API",
        docs_url="/docs",
        openapi_url="/openapi.json"
    )
    app.include_router(api_router)
    return app
```

Benefits:
- Easy to create multiple app instances for testing
- Clean separation of configuration
- Testability without side effects

---

## Database Architecture

### Session Management

Database sessions are managed using **dependency injection**:

```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# app/api/deps.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Routes depend on `get_db()`:
```python
@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()
```

### ORM Models

SQLAlchemy 2.0 models use declarative mapping:

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
```

---

## Security Architecture

### JWT Token Flow

1. User logs in with credentials
2. Backend validates password with Argon2
3. JWT tokens generated:
   - Access token (30 min expiry)
   - Refresh token (7 days expiry)
4. Client stores tokens
5. Client sends access token in Authorization header
6. Backend validates token signature and expiry
7. On expiry, client uses refresh token to get new access token

### Password Hashing

Argon2 is used for all password operations:

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

# Hash on registration
hashed = ph.hash("plain_password")

# Verify on login
try:
    ph.verify(stored_hash, provided_password)
except argon2.exceptions.VerifyMismatchError:
    # Wrong password
```

### RBAC Implementation

Authorization is enforced via **dependency injection**:

```python
# app/api/deps.py
def get_current_user_admin(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = verify_token_and_get_user(db, token)
    if user.role != "admin":
        raise HTTPException(status_code=403)
    return user
```

Usage in routes:
```python
@router.delete("/projects/{id}")
def delete_project(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_admin)
):
    # Only admins reach here
    ...
```

---

## Schema Validation

Pydantic schemas validate all inputs and outputs:

**Request Schema:**
```python
class ProjectCreate(BaseModel):
    title: str
    description: str
    github_url: str
    tag_ids: list[int] = []
```

**Response Schema:**
```python
class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
```

Benefits:
- Automatic validation
- Clear API contracts
- Auto-generated OpenAPI docs
- Type safety

---

## Dependency Injection

FastAPI's dependency injection system powers:

1. **Database Sessions**
   ```python
   db: Session = Depends(get_db)
   ```

2. **Authentication**
   ```python
   current_user = Depends(get_current_user)
   ```

3. **Authorization**
   ```python
   admin_user = Depends(get_current_user_admin)
   ```

This approach:
- Reduces code duplication
- Makes testing easier (override dependencies)
- Separates concerns cleanly

---

## Error Handling

FastAPI handles errors consistently:

```python
from fastapi import HTTPException

# Not found
raise HTTPException(status_code=404, detail="Project not found")

# Forbidden
raise HTTPException(status_code=403, detail="Not authorized")

# Bad request
raise HTTPException(status_code=400, detail="Invalid input")
```

Pydantic validation errors return 422 automatically.

---

## Testing Architecture

Tests use **dependency overrides** for isolation:

```python
# tests/conftest.py
def override_get_db():
    db = TestSessionLocal()  # SQLite in-memory
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
```

This allows:
- Fast tests (SQLite in-memory)
- No external dependencies
- Clean isolation per test

---

## Migration Strategy

Alembic manages database schema versions:

1. **Create Migration**
   ```bash
   alembic revision --autogenerate -m "add projects table"
   ```

2. **Review Generated Migration**
   Alembic compares models to database and generates upgrade/downgrade scripts.

3. **Apply Migration**
   ```bash
   alembic upgrade head
   ```

4. **Rollback if Needed**
   ```bash
   alembic downgrade -1
   ```

Migrations are versioned in `alembic/versions/` and tracked in the database.

---

## Multi-Tenancy Pattern

Every query is **scoped by organization ID**:

```python
# Always filter by org_id
projects = db.query(Project).filter(
    Project.org_id == current_user.org_id
).all()
```

This ensures:
- Data isolation between organizations
- No accidental cross-org data access
- Simple and explicit enforcement

---

## Separation of Concerns

| Layer | Responsibility | Example |
|-------|---------------|---------|
| **Routes** | HTTP handling, request/response | `app/api/routes/` |
| **Schemas** | Validation, serialization | `app/schemas/` |
| **Models** | Database structure | `app/models/` |
| **Services** | Business logic | `app/services/` |
| **Core** | Security, config | `app/core/` |
| **DB** | Database connection | `app/db/` |

This structure:
- Makes code easy to navigate
- Isolates changes
- Follows industry patterns

---

## Performance Considerations

### Database Queries
- Eager loading with `joinedload()` for relationships
- Indexes on frequently queried columns (email, org_id)
- Pagination for large result sets

### API Response Time
- FastAPI async support for I/O-bound operations
- Connection pooling via SQLAlchemy
- Minimal middleware overhead

### Caching
- No caching currently (data changes frequently)
- Future: Redis for frequently accessed data

---

## Why This Architecture

This architecture was chosen for:

1. **Clarity** - Easy for reviewers to understand
2. **Testability** - Dependency injection enables clean tests
3. **Security** - Multiple layers of validation and authorization
4. **Maintainability** - Clear separation of concerns
5. **Industry Standard** - Follows FastAPI best practices
6. **Scalability** - Can grow to handle more users and features

The focus is **correctness and code quality**, not premature optimization.
