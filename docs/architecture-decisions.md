# Architecture Decisions

This document captures key architectural and technical decisions made during the development of this project, including the rationale, alternatives considered, and trade-offs.

---

## 1. Framework Choice: FastAPI vs Flask vs Django

### Decision: Use FastAPI

**Context:**
- Need a modern Python web framework for building a RESTful API
- Must support JWT authentication, RBAC, and multi-tenancy
- Should have good performance and type safety

**Alternatives Considered:**
- **Django + Django REST Framework**: Full-featured web framework with ORM, admin panel, and batteries-included approach
- **Flask + Flask-RESTful**: Lightweight microframework with flexibility
- **FastAPI**: Modern, async framework with automatic OpenAPI docs

**Why FastAPI:**

1. **Performance**:
   - ASGI-based (asynchronous) vs WSGI (Flask/Django)
   - Comparable to Node.js and Go in benchmarks
   - Built on Starlette (fast web framework) and Pydantic (fast validation)

2. **Automatic Documentation**:
   - OpenAPI/Swagger UI auto-generated from code
   - No need to manually maintain API documentation
   - Interactive testing interface at `/docs`

3. **Type Safety**:
   - Python type hints everywhere
   - Pydantic models for validation
   - Better IDE support (autocomplete, type checking)

4. **Modern Python**:
   - Uses Python 3.10+ features (type hints, async/await)
   - Industry trend toward FastAPI (used by Microsoft, Uber, Netflix)
   - Active development and community

5. **Developer Experience**:
   - Less boilerplate than Django
   - Better structure than Flask (dependency injection, clear patterns)
   - Easy to test (dependency overrides)

**Trade-offs:**

| Aspect | FastAPI | Django | Flask |
|--------|---------|--------|-------|
| Async support | Native | Limited | Via plugins |
| Documentation | Auto-generated | Manual | Manual |
| ORM | Bring your own | Built-in | Bring your own |
| Admin panel | No | Built-in | Plugins |
| Learning curve | Medium | High | Low |
| Performance | Excellent | Good | Good |
| Type safety | Strong | Limited | Limited |

**When to Use Alternatives:**
- **Django**: If you need a full-stack framework with admin panel, forms, templates, and batteries-included philosophy
- **Flask**: If you want maximum flexibility and simplicity for small projects

**Conclusion:**
FastAPI provides the best balance of performance, developer experience, and modern Python features for building production-grade APIs.

---

## 2. ORM: SQLAlchemy 2.0

### Decision: Use SQLAlchemy 2.0 with type hints

**Why:**

1. **Industry Standard**:
   - Most popular Python ORM
   - Used by major companies (Reddit, Yelp, Dropbox)
   - Mature, battle-tested, well-documented

2. **SQLAlchemy 2.0 Features**:
   - Modern API with type hints (`Mapped[int]`)
   - Better type safety than 1.x
   - Cleaner query syntax
   - Forward-compatible with async (future enhancement)

3. **Database Agnostic**:
   - PostgreSQL in production
   - SQLite for tests
   - Easy to switch databases

4. **Power and Flexibility**:
   - Complex queries when needed
   - Relationships and joins
   - Migration support via Alembic

**Example:**
```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
```

**Alternatives:**
- **Django ORM**: Tied to Django framework
- **Tortoise ORM**: Async-first but less mature
- **Raw SQL**: Too low-level, no type safety

**Trade-offs:**
- More boilerplate than Django ORM
- Steeper learning curve
- Worth it for power and flexibility

---

## 3. Password Hashing: Argon2

### Decision: Use Argon2 for password hashing

**Why:**

1. **Security**:
   - Winner of the Password Hashing Competition (2015)
   - Resistant to GPU and ASIC attacks (memory-hard)
   - Configurable memory, time, and parallelism costs

2. **Modern Standard**:
   - Recommended by OWASP
   - Better than bcrypt and PBKDF2
   - Used by 1Password, Bitwarden, Microsoft

3. **Implementation**:
   - `argon2-cffi` is well-maintained Python library
   - Simple API (hash, verify)

**Example:**
```python
from argon2 import PasswordHasher

ph = PasswordHasher()
hashed = ph.hash("plain_password")
ph.verify(hashed, "plain_password")  # Returns True
```

**Alternatives:**
- **bcrypt**: Good but less memory-hard (easier to attack with GPUs)
- **PBKDF2**: Older, less resistant to attacks
- **scrypt**: Similar to Argon2 but less tested

**Trade-offs:**
- Argon2 uses more memory (by design, for security)
- Acceptable trade-off for significantly better security

---

## 4. Authentication: JWT with Refresh Tokens

### Decision: Implement JWT-based authentication with access + refresh tokens

**Why:**

1. **Stateless**:
   - No server-side session storage
   - Scales horizontally (no shared session state)
   - Works well with serverless/microservices

2. **Secure**:
   - Access tokens expire quickly (30 min)
   - Refresh tokens last longer (7 days)
   - Compromise of access token has limited impact

3. **Token Refresh**:
   - Client automatically refreshes expired access tokens
   - No user disruption every 30 minutes
   - Refresh token can be revoked if needed

**Implementation:**
```python
# Short-lived access token
access_token = create_access_token(
    subject=user.email,
    expires_delta=timedelta(minutes=30)
)

# Long-lived refresh token
refresh_token = create_refresh_token(
    subject=user.email,
    expires_delta=timedelta(days=7)
)
```

**Alternatives:**
- **Session-based auth**: Requires session storage (Redis/database)
- **OAuth2 with external provider**: Overkill for this project
- **API keys**: Less secure, no expiry

**Trade-offs:**
- Can't revoke JWT tokens before expiry (without token blacklist)
- Acceptable for educational project
- Production: Add token blacklist in Redis for logout

---

## 5. Database Migrations: Alembic

### Decision: Use Alembic for database migrations

**Why:**

1. **SQLAlchemy Integration**:
   - Official migration tool for SQLAlchemy
   - Seamless integration with ORM models
   - Auto-generates migrations by comparing models to schema

2. **Version Control**:
   - Migrations are code (tracked in Git)
   - Upgrade and downgrade scripts
   - Team collaboration (merge migrations)

3. **Safety**:
   - Review migrations before applying
   - Test migrations in development
   - Rollback if something goes wrong

**Example Workflow:**
```bash
# Create migration
alembic revision --autogenerate -m "add projects table"

# Review generated migration file
# Edit if needed

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

**Alternatives:**
- **Django migrations**: Tied to Django
- **Flyway**: Java-based, not Python-native
- **Manual SQL**: Error-prone, no version tracking

---

## 6. Testing Framework: Pytest

### Decision: Use pytest for all tests

**Why:**

1. **Modern and Powerful**:
   - Fixture system for setup/teardown
   - Parametrized tests
   - Better error messages than unittest

2. **FastAPI Integration**:
   - TestClient works seamlessly with pytest
   - Dependency overrides for clean tests

3. **Developer Experience**:
   - Simple `assert` statements (no `self.assertEqual`)
   - Plugins for coverage, parallel execution
   - Industry standard

**Example:**
```python
def test_create_project(client, admin_token_headers):
    response = client.post(
        "/projects",
        json={"title": "Test", "description": "Test"},
        headers=admin_token_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test"
```

**Alternatives:**
- **unittest**: Verbose, older style
- **nose**: Deprecated
- **pytest** is the clear choice

---

## 7. Test Database: SQLite In-Memory

### Decision: Use SQLite in-memory for tests

**Why:**

1. **Speed**:
   - No disk I/O
   - Tests run in ~1 second
   - Fresh database for each test session

2. **Isolation**:
   - No shared state between tests
   - No cleanup needed
   - Deterministic results

3. **Simplicity**:
   - No external dependencies
   - Works on CI without setup
   - Same SQLAlchemy code as production

**Implementation:**
```python
# tests/conftest.py
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL)
```

**Trade-offs:**
- SQLite has some differences from PostgreSQL
- Acceptable for integration tests
- Critical queries tested manually with PostgreSQL

---

## 8. Configuration Management: Pydantic Settings

### Decision: Use Pydantic `BaseSettings` for configuration

**Why:**

1. **Type Safety**:
   - Environment variables are validated
   - Type conversions automatic
   - Clear error messages for missing config

2. **Development Experience**:
   - `.env` file support
   - Defaults for local development
   - Override in production

**Example:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
```

**Alternatives:**
- **python-decouple**: Less type-safe
- **os.getenv()**: No validation
- **configparser**: Too verbose

---

## 9. API Versioning: No Versioning (Yet)

### Decision: Start without API versioning

**Why:**

1. **YAGNI Principle**:
   - You Aren't Gonna Need It
   - No clients currently depend on API
   - Versioning adds complexity

2. **Future-Proofing**:
   - Can add versioning later if needed
   - Would use URL versioning (`/v1/projects`)

**When to Add Versioning:**
- Multiple clients consuming the API
- Breaking changes needed
- Public API with SLAs

---

## 10. Error Response Format: FastAPI Default

### Decision: Use FastAPI's default error format

**Why:**

1. **Consistency**:
   - All errors follow same structure
   - `{"detail": "error message"}`
   - Industry-standard format

2. **Validation Errors**:
   - Pydantic validation errors are detailed
   - Shows exactly which fields are invalid

**Example Responses:**
```json
// 404 Not Found
{"detail": "Project not found"}

// 403 Forbidden
{"detail": "Not authorized"}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 11. CORS Policy: Restrictive

### Decision: Allow CORS only for frontend origin

**Why:**

1. **Security**:
   - Prevent unauthorized origins from calling API
   - Only frontend can make requests

2. **Production**:
   - Configure allowed origins in environment
   - Never use `origins=["*"]`

**Implementation:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 12. Logging Strategy: Minimal (For Now)

### Decision: Use Python's built-in logging sparingly

**Why:**

1. **Development**:
   - FastAPI's auto-reload shows errors
   - Swagger UI for API testing
   - Logs add noise during development

2. **Production**:
   - Would add structured logging (JSON logs)
   - Would use logging service (CloudWatch, Datadog)

**Future Enhancement:**
```python
import logging

logger = logging.getLogger(__name__)
logger.info("User logged in", extra={"user_id": user.id})
```

---

## 13. CI/CD: GitHub Actions

### Decision: Use GitHub Actions for CI

**Why:**

1. **Native Integration**:
   - Built into GitHub
   - No external service needed
   - Free for public repos

2. **Simple Workflow**:
   - Install dependencies
   - Run tests
   - Fail on errors

**Future Deployment:**
- Would add deployment to Heroku/Railway/Fly.io
- Would add Docker image build
- Would add environment-specific tests

---

## Summary of Key Principles

1. **Modern Python**: Use latest features (3.13, type hints, async)
2. **Type Safety**: Pydantic and SQLAlchemy 2.0 for strong typing
3. **Security First**: Argon2, JWT, RBAC, input validation
4. **Developer Experience**: FastAPI DX, pytest, auto-docs
5. **Simplicity**: YAGNI principle, avoid over-engineering
6. **Industry Standards**: Follow best practices from production systems
7. **Testability**: Dependency injection, fixture-based tests

---

## Future Considerations

As the application grows, these architectural changes might become necessary:

### If Traffic Grows to 10,000+ Requests/Hour:
- Add Redis for caching frequent queries
- Implement database read replicas
- Add API rate limiting per user/IP

### If Team Grows to 5+ Developers:
- Add pre-commit hooks (black, flake8, mypy)
- Implement code review guidelines
- Add integration with Sentry for error tracking

### If Feature Complexity Grows:
- Add background task queue (Celery + Redis)
- Implement event sourcing for audit logs
- Add full-text search (Elasticsearch)

### If Security Requirements Increase:
- Implement token blacklist for logout
- Add 2FA (TOTP)
- Implement API key authentication for third-party integrations
- Add request/response encryption

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Argon2 Password Hashing](https://github.com/P-H-C/phc-winner-argon2)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Twelve-Factor App](https://12factor.net/)
