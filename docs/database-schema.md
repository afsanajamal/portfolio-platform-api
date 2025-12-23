# Database Schema

## Core Tables

### organizations
- id
- name
- created_at

Each organization is isolated from others.

---

### users
- id
- org_id (FK)
- email
- hashed_password
- role

Users always belong to exactly one organization.

---

### projects
- id
- org_id (FK)
- owner_id (FK → users)
- title
- description
- github_url
- is_public

Projects are scoped to an organization.

---

### tags
- id
- org_id (FK)
- name

---

### project_tags
Many-to-many relationship between projects and tags.

---

### activity_logs
- id
- org_id (FK)
- actor_user_id
- action
- entity
- entity_id
- created_at

Used for audit logging.

---

## Multi-Tenancy Strategy

- Every major table includes `org_id`
- Queries are always scoped by `org_id`
- Prevents cross-organization data access

This approach is simple, explicit, and reliable.
