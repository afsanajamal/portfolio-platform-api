# Project & Portfolio Platform API

A production-style backend API for managing projects and portfolios in a multi-tenant environment.
Built with FastAPI and PostgreSQL, featuring JWT authentication, role-based access control (RBAC), audit logs, and automated tests.

This project is designed as a **portfolio-quality backend system**, suitable for academic evaluation and backend team review.

---

## Tech Stack

- **Backend Framework**: FastAPI
- **Language**: Python 3.13
- **Database**: PostgreSQL (Dockerized for local development)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT (Access + Refresh tokens)
- **Password Hashing**: Argon2
- **Authorization**: Role-Based Access Control (RBAC)
- **Testing**: Pytest + FastAPI TestClient
- **API Documentation**: OpenAPI / Swagger
- **CI/CD**: GitHub Actions

---

## Core Features

### Authentication & Security
- User registration and login
- OAuth2 password flow
- JWT-based authentication (access & refresh tokens)
- Secure password hashing using Argon2
- Token refresh mechanism for seamless user experience

### Authorization (RBAC)
- **Admin**
  - Manage users and organizations
  - Full CRUD access to all projects
  - Access audit logs
  - Delete any project
- **Editor**
  - Create and update projects
  - Edit/delete own projects only
  - Create tags
- **Viewer**
  - Read-only access to projects and tags
  - No create/edit/delete permissions

### Project Management
- Create and manage projects within an organization
- Tag-based project categorization
- Public / private project visibility
- Multi-tenant organization support
- Project ownership and access control

### Tag Management
- Create and manage project tags
- Tag-based filtering
- Role-based tag creation (admin/editor only)

### Audit Logging
- Automatic activity logs for sensitive actions (e.g. project creation, user management)
- Admin-only access to audit logs
- Track who did what and when

### Testing
- 15+ comprehensive integration tests
- Isolated test database (SQLite in-memory)
- Auth, RBAC, and project CRUD tested
- Edge case and error handling tests
- GitHub Actions CI running on every push

---

## Documentation

Detailed project documentation is available below:

- [Project Overview](docs/overview.md) - Project goals, features, and scope
- [Architecture & Structure](docs/architecture.md) - Technical architecture and patterns
- [Architecture Decisions](docs/architecture-decisions.md) - Why we chose FastAPI, SQLAlchemy, Argon2, etc.
- [API Endpoints](docs/api-endpoints.md) - Complete API reference with examples
- [Authentication & RBAC](docs/auth-and-rbac.md) - Security implementation details
- [Database Schema](docs/database-schema.md) - Database structure and relationships
- [Testing & CI](docs/testing-and-ci.md) - Testing strategy and continuous integration
- [Development Guide](docs/development.md) - Setup instructions and common tasks

---

## Quick Start

### Prerequisites

- Python 3.13+
- Docker and Docker Compose (for PostgreSQL)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/afsanajamal/portfolio-platform-api.git
   cd portfolio-platform-api
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Update `.env` with your configuration (defaults work for local development):
   ```env
   DATABASE_URL=postgresql+psycopg://portfolio:portfolio@localhost:5432/portfolio_db
   JWT_SECRET=your-secret-key-change-this-in-production
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

5. **Start PostgreSQL with Docker**
   ```bash
   docker-compose up -d
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Seed test data**
   ```bash
   PYTHONPATH=. python scripts/seed_admin.py
   ```

8. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

9. **Open API documentation**
   ```
   http://127.0.0.1:8000/docs
   ```

---

## Available Scripts

### Development
- `uvicorn app.main:app --reload` – Start development server with auto-reload
- `uvicorn app.main:app --host 0.0.0.0 --port 8000` – Start server on custom host/port

### Testing
- `pytest` – Run all tests
- `pytest -v` – Run tests with verbose output
- `pytest --cov=app` – Run tests with coverage report
- `pytest tests/test_auth.py` – Run specific test file
- `pytest -x` – Stop on first failure

### Database
- `alembic upgrade head` – Apply all migrations
- `alembic downgrade -1` – Rollback one migration
- `alembic revision --autogenerate -m "message"` – Create new migration
- `alembic history` – Show migration history

### Utilities
- `PYTHONPATH=. python scripts/seed_admin.py` – Seed test users and organizations

---

## Test Accounts

For testing purposes, use these accounts (seeded via `scripts/seed_admin.py`):

| Role   | Email                    | Password      |
|--------|--------------------------|---------------|
| Admin  | admin@example.com        | admin12345    |
| Editor | editor@example.com       | editor12345   |
| Viewer | viewer@example.com       | viewer12345   |

---

## Project Structure

```
portfolio-platform-api/
├── app/                        # Main application code
│   ├── api/                    # API routes and dependencies
│   │   ├── deps.py            # Dependency injection (auth, RBAC)
│   │   ├── router.py          # Main API router
│   │   └── routes/            # Route handlers
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── users.py       # User management
│   │       ├── projects.py    # Project CRUD
│   │       ├── tags.py        # Tag management
│   │       ├── activity.py    # Audit logs
│   │       └── orgs.py        # Organization management
│   ├── core/                   # Core utilities
│   │   ├── config.py          # Configuration settings
│   │   └── security.py        # JWT & password hashing
│   ├── db/                     # Database configuration
│   │   ├── base.py            # SQLAlchemy base
│   │   └── session.py         # Database session
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py            # User model
│   │   ├── organization.py    # Organization model
│   │   ├── project.py         # Project model
│   │   ├── tag.py             # Tag model
│   │   ├── activity.py        # Activity log model
│   │   └── enums.py           # Enum definitions (roles)
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py            # Auth request/response schemas
│   │   ├── user.py            # User schemas
│   │   ├── project.py         # Project schemas
│   │   ├── tag.py             # Tag schemas
│   │   ├── activity.py        # Activity log schemas
│   │   └── org.py             # Organization schemas
│   ├── services/               # Business logic
│   │   ├── activity_service.py # Activity logging
│   │   └── tag_service.py     # Tag operations
│   └── main.py                 # FastAPI application entry point
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Alembic configuration
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest fixtures
│   ├── test_auth.py           # Authentication tests
│   ├── test_rbac_projects.py  # RBAC tests
│   ├── test_tags.py           # Tag tests
│   ├── test_admin.py          # Admin functionality tests
│   └── test_edge_cases.py     # Edge case tests
├── scripts/                    # Utility scripts
│   └── seed_admin.py          # Database seeding
├── docs/                       # Documentation
├── .env.example                # Environment variables template
├── .github/                    # GitHub Actions CI
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # PostgreSQL container
├── pytest.ini                  # Pytest configuration
└── requirements.txt            # Python dependencies
```

---

## Key Technologies Explained

### FastAPI
- Modern, high-performance web framework
- Automatic interactive API documentation (Swagger/ReDoc)
- Built-in data validation with Pydantic
- Native async support for better performance
- Type hints for better IDE support

### JWT Authentication
- Access tokens (short-lived, 30 min) for API requests
- Refresh tokens (long-lived, 7 days) for token renewal
- Secure token-based authentication without server-side sessions
- Automatic token expiry and refresh mechanism

### SQLAlchemy 2.0
- Modern ORM with full type hint support
- Declarative models with relationship mapping
- Query builder for complex database operations
- Database-agnostic (PostgreSQL in production, SQLite for tests)

### Alembic
- Database migration management
- Version control for database schema
- Auto-generate migrations from model changes
- Safe rollback capabilities

### Argon2
- Memory-hard password hashing algorithm
- Resistant to GPU-based attacks
- Winner of the Password Hashing Competition
- More secure than bcrypt or PBKDF2

### Pytest
- Powerful testing framework with fixtures
- Integration testing with FastAPI TestClient
- In-memory SQLite for fast, isolated tests
- Coverage reporting for test quality metrics

---

## CI/CD

GitHub Actions automatically:
- Runs all tests on every push
- Validates code quality
- Ensures database migrations are valid
- Fails build on test failures or errors

See [Testing & CI](docs/testing-and-ci.md) for details.

---

## API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
  - Interactive API testing interface
  - Try out endpoints directly in browser
  - View request/response schemas

- **ReDoc**: http://127.0.0.1:8000/redoc
  - Alternative documentation interface
  - Better for reading and sharing

- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json
  - Raw OpenAPI 3.0 specification
  - Can be imported into Postman, Insomnia, etc.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project was created for portfolio and educational purposes.

