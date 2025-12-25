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

---

## Core Features

### Authentication & Security
- User registration and login
- OAuth2 password flow
- JWT-based authentication (access & refresh tokens)
- Secure password hashing using Argon2

### Authorization (RBAC)
- **Admin**
  - Manage users
  - Create, update, and view projects
  - Access audit logs
- **Editor**
  - Create and update projects
- **Viewer**
  - Read-only access to public projects

### Project Management
- Create and manage projects within an organization
- Tag-based project categorization
- Public / private project visibility
- Multi-tenant organization support

### Audit Logging
- Automatic activity logs for sensitive actions (e.g. project creation)
- Admin-only access to audit logs

### Testing
- Isolated test database (SQLite)
- Integration-style API tests
- Auth, RBAC, and project CRUD tested
- Dependency overrides for clean test isolation

---

## Project Structure

## Documentation

Detailed project documentation is available below:

- [Project Overview](docs/overview.md)
- [Architecture & Design Decisions](docs/architecture.md)
- [Authentication & RBAC](docs/auth-and-rbac.md)
- [Database Schema](docs/database-schema.md)
- [Testing & CI](docs/testing-and-ci.md)
- [Development Guide](docs/development.md)


