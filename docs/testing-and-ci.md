# Testing & CI

## Testing Strategy

The project uses **integration-style tests** rather than heavy mocking.

Key ideas:
- Test real API behavior
- Validate auth, RBAC, and DB interactions
- Avoid testing framework internals

---

## Test Setup

- SQLite is used as a test database
- Database schema is created fresh for tests
- FastAPI dependencies are overridden

This ensures:
- Fast tests
- No external services required
- Deterministic results

---

## Covered Scenarios

- User registration & login
- JWT authentication
- Role-based access control
- Forbidden access cases
- Project CRUD operations
- Auth-required endpoints

---

## Continuous Integration

GitHub Actions is configured to:
- Install dependencies
- Run pytest on every push and PR
- Fail builds if tests fail

Environment variables are injected directly in CI to avoid secrets leakage.

---

## Why This Matters

Testing and CI ensure:
- Code quality
- Confidence in changes
- Professional engineering workflow

This mirrors real backend team practices.
