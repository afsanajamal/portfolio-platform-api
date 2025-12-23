# Project Overview

This project is a backend API for a **multi-tenant project & portfolio platform**.

The system allows organizations to manage users and projects with strict role-based access control (RBAC).  
It is designed to demonstrate **real-world backend engineering practices**, not tutorial-level examples.

The API supports:
- Authentication using JWT
- Role-based authorization (admin / editor / viewer)
- Project and tag management
- Audit logging
- Automated testing and CI

This project was built as:
- A backend portfolio project
- Preparation for backend team responsibilities
- Supporting material for postgraduate (Master’s) applications

---

## Core Use Case

Each **organization** can:
- Register once (creates an admin)
- Add users with specific roles
- Manage projects internally
- Control who can create, edit, or view data

Users **cannot access data from other organizations**.

---

## Key Goals

- Demonstrate backend fundamentals clearly
- Use production-style architecture
- Enforce security at the API level
- Keep the codebase testable and maintainable

---

## Non-Goals

- Frontend UI (handled in a separate project)
- Advanced performance optimization
- External integrations

The focus is correctness, clarity, and backend design.
