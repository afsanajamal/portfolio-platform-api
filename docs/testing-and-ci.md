# Testing & CI

## Testing Strategy

The project uses **integration-style tests** rather than heavy unit testing or mocking.

Key principles:
- Test real API behavior with actual database
- Validate auth, RBAC, and database interactions
- Avoid testing framework internals (FastAPI, SQLAlchemy)
- Focus on user-facing functionality and edge cases

This approach ensures tests catch real bugs and regression, not just verify mocks.

---

## Test Framework

- **pytest**: Modern Python testing framework
- **FastAPI TestClient**: In-process HTTP client for API testing
- **SQLite in-memory**: Fast, isolated test database
- **Fixtures**: Reusable test setup (client, DB, auth tokens)

---

## Test Setup

### Database Isolation

Tests use SQLite in-memory instead of PostgreSQL:

```python
# tests/conftest.py
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL)
```

Benefits:
- **Fast**: No disk I/O, tests run in ~1 second
- **Isolated**: Fresh database for each test session
- **No cleanup**: Database destroyed after tests
- **CI-friendly**: No external dependencies

### Dependency Overrides

FastAPI's dependency injection is overridden for tests:

```python
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
```

This allows:
- Tests to use in-memory SQLite
- Clean isolation per test run
- No pollution of production database

### Test Fixtures

Fixtures in `tests/conftest.py` provide reusable test setup:

- `client`: FastAPI TestClient for making API requests
- `db`: Test database session
- `admin_token_headers`: Authenticated admin user
- `editor_token_headers`: Authenticated editor user
- `viewer_token_headers`: Authenticated viewer user

Example usage:
```python
def test_create_project(client, admin_token_headers):
    response = client.post(
        "/projects",
        json={"title": "Test Project", "description": "Test"},
        headers=admin_token_headers
    )
    assert response.status_code == 200
```

---

## Test Coverage

### Total Tests: 15+

Tests are organized by feature:

#### Authentication Tests (`tests/test_auth.py`)
1. **Register user** - Creates organization and admin
2. **Login with valid credentials** - Returns access and refresh tokens
3. **Login with invalid credentials** - Returns 401
4. **Refresh token** - Gets new access token
5. **Refresh with invalid token** - Returns 401

#### RBAC Tests (`tests/test_rbac_projects.py`)
6. **Admin can create project** - Success
7. **Editor can create project** - Success
8. **Viewer cannot create project** - Returns 403
9. **Admin can delete any project** - Success
10. **Editor can delete own project** - Success
11. **Editor cannot delete other's project** - Returns 403
12. **Viewer cannot delete any project** - Returns 403

#### Tag Tests (`tests/test_tags.py`)
13. **List tags** - All roles can view
14. **Create tag as editor** - Success
15. **Viewer cannot create tag** - Returns 403

#### Admin Tests (`tests/test_admin.py`)
- Admin-only endpoints (users, activity logs)
- Non-admin access blocked

#### Edge Case Tests (`tests/test_edge_cases.py`)
- Invalid inputs
- Missing fields
- Duplicate resources
- Cross-organization access attempts

---

## Test Categories

### By Type

| Category | Tests | Purpose |
|----------|-------|---------|
| Authentication | 5 | Login, register, token refresh |
| RBAC Enforcement | 7 | Role-based permissions |
| Projects CRUD | 4 | Create, read, update, delete |
| Tags | 3 | Tag management |
| Admin Features | 2 | User management, activity logs |
| **Total** | **15+** | **Comprehensive coverage** |

### By HTTP Status

| Status Code | Scenarios Tested |
|-------------|------------------|
| 200 OK | Successful operations |
| 401 Unauthorized | Invalid/missing auth tokens |
| 403 Forbidden | RBAC violations |
| 404 Not Found | Non-existent resources |
| 422 Unprocessable Entity | Validation errors |

---

## Running Tests

### All Tests
```bash
pytest
```

### With Verbose Output
```bash
pytest -v
```

### With Coverage Report
```bash
pytest --cov=app
pytest --cov=app --cov-report=html  # HTML coverage report
```

### Specific Test File
```bash
pytest tests/test_auth.py
```

### Specific Test Function
```bash
pytest tests/test_auth.py::test_login_success
```

### Stop on First Failure
```bash
pytest -x
```

### Show Print Statements
```bash
pytest -s
```

---

## Test Examples

### Authentication Test
```python
def test_login_success(client):
    # Register user first
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "test12345",
        "org_name": "Test Org"
    })

    # Login
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "test12345"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
```

### RBAC Test
```python
def test_viewer_cannot_create_project(client, viewer_token_headers):
    response = client.post(
        "/projects",
        json={"title": "Test", "description": "Test", "github_url": "https://github.com/test/test"},
        headers=viewer_token_headers
    )
    assert response.status_code == 403
```

### Edge Case Test
```python
def test_duplicate_email_registration(client):
    # Register once
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "test12345",
        "org_name": "Test Org"
    })

    # Try to register again
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "different123",
        "org_name": "Different Org"
    })

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()
```

---

## Continuous Integration (GitHub Actions)

### Workflow: `.github/workflows/ci.yml`

On every push and pull request to `main`:

#### Step 1: Setup Environment
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.13'
```

#### Step 2: Install Dependencies
```yaml
- name: Install dependencies
  run: |
    pip install --upgrade pip
    pip install -r requirements.txt
```

#### Step 3: Run Tests
```yaml
- name: Run tests with coverage
  run: |
    pytest -v --cov=app --cov-report=term
```

#### Step 4: Build Status
- ✅ **Pass**: All tests pass, PR can be merged
- ❌ **Fail**: Tests failed, PR blocked

### CI Configuration

Environment variables for CI:
```yaml
env:
  DATABASE_URL: sqlite:///:memory:
  JWT_SECRET: test-secret
  JWT_ALGORITHM: HS256
  ACCESS_TOKEN_EXPIRE_MINUTES: "30"
  REFRESH_TOKEN_EXPIRE_DAYS: "7"
```

Benefits:
- No secrets in repository
- Reproducible builds
- Fast feedback on PRs

---

## Test Best Practices

### ✅ Do

1. **Test user-facing behavior**, not implementation
   ```python
   # Good: Test API response
   assert response.status_code == 200
   assert response.json()["title"] == "Project"

   # Avoid: Test internal details
   # assert db.query(Project).count() == 1  # Implementation detail
   ```

2. **Use descriptive test names**
   ```python
   # Good
   def test_editor_can_create_project():
       ...

   # Avoid
   def test_project_1():
       ...
   ```

3. **Test edge cases**
   - Invalid inputs
   - Missing required fields
   - Duplicate data
   - Cross-organization access

4. **Use fixtures for reusable setup**
   ```python
   @pytest.fixture
   def admin_user(client):
       # Setup code
       return user
   ```

### ❌ Avoid

1. **Over-mocking** - Use real database, not mocks
2. **Testing framework internals** - Don't test FastAPI/SQLAlchemy
3. **Flaky tests** - Ensure deterministic results
4. **Test interdependence** - Each test should run independently

---

## Coverage Goals

### Current Coverage
- **Auth**: 100% (all flows tested)
- **RBAC**: 100% (all permission combinations)
- **Projects**: 90%+ (CRUD operations)
- **Tags**: 90%+
- **Overall**: 85%+

### Areas Not Tested
- Error logging internals
- Database connection pooling
- CORS middleware

These are framework-level features that don't need testing.

---

## Future Testing Enhancements

### Load Testing
- Use Locust or k6 for performance testing
- Test 1000+ concurrent requests
- Identify bottlenecks

### Security Testing
- SQL injection attempts (should be blocked by ORM)
- XSS attempts (should be blocked by Pydantic)
- CSRF (not applicable for stateless API)

### Integration Testing with Frontend
- End-to-end tests with real frontend
- Playwright tests against running API

---

## Why Testing Matters

1. **Confidence in Changes**
   - Refactor without fear
   - Add features knowing existing ones work
   - Catch regressions before production

2. **Documentation**
   - Tests show how API should be used
   - Examples for new developers
   - Living documentation that can't go stale

3. **Professional Workflow**
   - Industry-standard practice
   - Required for team collaboration
   - Shows code quality awareness

4. **Security**
   - RBAC must be tested rigorously
   - Critical that viewers can't edit
   - No authentication bypass

This testing strategy ensures **production-quality code** suitable for real-world deployment.
