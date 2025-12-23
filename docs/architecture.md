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
    ...
