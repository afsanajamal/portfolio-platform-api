# Project Overview

This project is a backend API for a **multi-tenant project & portfolio platform**.

The system allows organizations to manage users and projects with strict role-based access control (RBAC).
It is designed to demonstrate **real-world backend engineering practices**, not tutorial-level examples.

The API supports:
- JWT-based authentication with automatic token refresh
- Role-based authorization (admin / editor / viewer)
- Project and tag management
- Multi-tenant organization isolation
- Audit logging for compliance
- Comprehensive automated testing
- Continuous integration with GitHub Actions

This project was built as:
- A backend portfolio project showcasing production-quality code
- Preparation for backend team responsibilities
- Supporting material for postgraduate (Master's) applications
- Demonstration of modern Python/FastAPI development practices

---

## Core Use Case

Each **organization** can:
- Register once (creates an admin user automatically)
- Add users with specific roles (editor, viewer)
- Manage projects internally with full CRUD operations
- Organize projects with tags
- Control who can create, edit, or view data via RBAC
- Track all actions via audit logs (admin only)

Users **cannot access data from other organizations** - strict data isolation is enforced at the database query level.

---

## Key Features

### Authentication & Session Management
- User registration with organization creation
- Secure login with Argon2 password hashing
- JWT access tokens (30-minute expiry)
- JWT refresh tokens (7-day expiry)
- Automatic token refresh for seamless UX
- Stateless authentication (no server-side sessions)

### Authorization & RBAC
- **Admin**: Full control over organization, users, projects, and audit logs
- **Editor**: Create and manage own projects, create tags
- **Viewer**: Read-only access to projects and tags

### Project Management
- Create projects with title, description, GitHub URL
- Tag projects for categorization
- Public/private visibility flags
- Project ownership tracking
- Multi-tenant scoping (org-level isolation)

### Tag System
- Create and manage tags for project categorization
- Organization-scoped tags
- Many-to-many relationship with projects

### Audit Logging
- Automatic logging of sensitive actions (CREATE, UPDATE, DELETE)
- Track actor, entity, and timestamp
- Admin-only access for compliance

### Testing & Quality
- 15+ integration tests covering all major features
- Auth flow testing (register, login, token refresh)
- RBAC enforcement testing
- Edge case and error handling tests
- GitHub Actions CI running on every push
- SQLite in-memory tests for speed

---

## Target Audience

This project is intended for:

1. **Academic Reviewers** (Master's program applications)
   - Demonstrates software engineering fundamentals
   - Shows understanding of security, testing, and architecture

2. **Backend Engineering Teams**
   - Portfolio evaluation for hiring
   - Code quality and best practices assessment

3. **Technical Learners**
   - Example of production-quality FastAPI application
   - Reference for JWT auth, RBAC, and multi-tenancy patterns

4. **API Consumers**
   - Frontend developers building UIs for this API
   - See [API Endpoints Documentation](api-endpoints.md)

---

## Key Goals

1. **Demonstrate Backend Fundamentals Clearly**
   - RESTful API design
   - Database modeling with relationships
   - Authentication and authorization
   - Input validation and error handling

2. **Use Production-Style Architecture**
   - Dependency injection for testability
   - Separation of concerns (routes, schemas, models, services)
   - Database migrations with version control
   - Environment-based configuration

3. **Enforce Security at the API Level**
   - Never trust client input
   - Server-side RBAC enforcement
   - Secure password hashing (Argon2)
   - JWT token expiry and refresh

4. **Keep the Codebase Testable and Maintainable**
   - Comprehensive test coverage
   - Clear code organization
   - Type hints throughout
   - Detailed documentation

5. **Follow Industry Best Practices**
   - FastAPI conventions
   - SQLAlchemy 2.0 patterns
   - pytest testing patterns
   - CI/CD with GitHub Actions

---

## Non-Goals

1. **Frontend UI** (handled in a separate project: [portfolio-platform-web](https://github.com/afsanajamal/portfolio-platform-web))
2. **Advanced Performance Optimization** (no caching, CDN, load balancing)
3. **External Integrations** (no OAuth providers, email services, payment systems)
4. **Real-Time Features** (no WebSockets, Server-Sent Events)
5. **Microservices Architecture** (monolithic API is intentional for simplicity)

The focus is **correctness, clarity, and backend design**, not scale or feature completeness.

---

## Technology Stack Summary

- **Framework**: FastAPI (async, type-safe, auto-documented)
- **Language**: Python 3.13 with type hints
- **Database**: PostgreSQL (production), SQLite (tests)
- **ORM**: SQLAlchemy 2.0 with type-mapped models
- **Migrations**: Alembic for version-controlled schema changes
- **Auth**: JWT tokens with Argon2 password hashing
- **Testing**: Pytest with FastAPI TestClient
- **CI**: GitHub Actions
- **Documentation**: OpenAPI/Swagger auto-generated

---

## Project Scope

### Included
✅ User authentication and authorization
✅ Project CRUD operations
✅ Tag management
✅ Audit logging
✅ Multi-tenancy
✅ RBAC enforcement
✅ Comprehensive tests
✅ API documentation

### Not Included (Future Enhancements)
❌ Email notifications
❌ File uploads (project images)
❌ Search and filtering
❌ Rate limiting
❌ Caching layer
❌ Background job processing

---

## Success Criteria

This project successfully demonstrates:

1. ✅ **Security**: No authentication bypass, RBAC enforced server-side
2. ✅ **Code Quality**: Type-safe, well-organized, documented
3. ✅ **Testing**: High coverage with meaningful tests
4. ✅ **Architecture**: Clear separation of concerns, maintainable
5. ✅ **Documentation**: README, architecture docs, API reference
6. ✅ **CI/CD**: Automated testing on every commit
7. ✅ **Industry Practices**: Follows FastAPI and Python best practices

---

## Getting Started

See [Development Guide](development.md) for setup instructions.

For API endpoint reference, see [API Endpoints](api-endpoints.md).

For architecture details, see [Architecture](architecture.md) and [Architecture Decisions](architecture-decisions.md).
