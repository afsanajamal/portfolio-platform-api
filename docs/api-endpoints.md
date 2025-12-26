# API Endpoints

Complete reference for all API endpoints, including request/response formats, authentication requirements, and RBAC enforcement.

**Base URL**: `http://127.0.0.1:8000`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Projects](#projects)
3. [Tags](#tags)
4. [Users](#users)
5. [Activity Logs](#activity-logs)
6. [Organizations](#organizations)

---

## Authentication

### Register User

Create a new organization and admin user (organization registration).

**Endpoint**: `POST /auth/register`

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "admin@example.com",
  "password": "securepassword123",
  "org_name": "My Organization"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "admin@example.com",
  "role": "admin",
  "org_id": 1,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors**:
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Invalid input (e.g., password too short)

---

### Login

Authenticate and receive JWT tokens.

**Endpoint**: `POST /auth/login`

**Authentication**: None (public endpoint)

**Request Body** (OAuth2 password flow):
```
username=admin@example.com&password=securepassword123
```

**Headers**:
```
Content-Type: application/x-www-form-urlencoded
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "role": "admin",
  "org_id": 1,
  "user_id": 1
}
```

**Errors**:
- `401 Unauthorized`: Invalid credentials

---

### Refresh Token

Get a new access token using refresh token.

**Endpoint**: `POST /auth/refresh`

**Authentication**: None (uses refresh token in body)

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "role": "admin",
  "org_id": 1,
  "user_id": 1
}
```

**Errors**:
- `401 Unauthorized`: Invalid or expired refresh token

---

## Projects

All project endpoints require authentication. Responses are scoped to the user's organization.

### List Projects

Get all projects in the user's organization.

**Endpoint**: `GET /projects`

**Authentication**: Required (all roles)

**RBAC**: Admin, Editor, Viewer

**Query Parameters**: None

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Portfolio Website",
    "description": "My personal portfolio built with Next.js",
    "github_url": "https://github.com/user/portfolio",
    "is_public": true,
    "owner_id": 1,
    "org_id": 1,
    "tags": [
      {"id": 1, "name": "Next.js"},
      {"id": 2, "name": "TypeScript"}
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### Get Project

Get a single project by ID.

**Endpoint**: `GET /projects/{id}`

**Authentication**: Required (all roles)

**RBAC**: Admin, Editor, Viewer (must belong to same organization)

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Portfolio Website",
  "description": "My personal portfolio built with Next.js",
  "github_url": "https://github.com/user/portfolio",
  "is_public": true,
  "owner_id": 1,
  "org_id": 1,
  "tags": [
    {"id": 1, "name": "Next.js"},
    {"id": 2, "name": "TypeScript"}
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors**:
- `404 Not Found`: Project doesn't exist or not in user's organization

---

### Create Project

Create a new project.

**Endpoint**: `POST /projects`

**Authentication**: Required

**RBAC**: Admin, Editor

**Request Body**:
```json
{
  "title": "New Project",
  "description": "Project description",
  "github_url": "https://github.com/user/project",
  "is_public": true,
  "tag_ids": [1, 2]
}
```

**Response** (200 OK):
```json
{
  "id": 2,
  "title": "New Project",
  "description": "Project description",
  "github_url": "https://github.com/user/project",
  "is_public": true,
  "owner_id": 1,
  "org_id": 1,
  "tags": [
    {"id": 1, "name": "Next.js"},
    {"id": 2, "name": "TypeScript"}
  ],
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Errors**:
- `403 Forbidden`: Viewer role attempting to create
- `422 Unprocessable Entity`: Invalid input (e.g., missing required fields)

---

### Update Project

Update an existing project.

**Endpoint**: `PUT /projects/{id}`

**Authentication**: Required

**RBAC**:
- Admin: Can update any project
- Editor: Can only update own projects
- Viewer: Cannot update

**Request Body**:
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "github_url": "https://github.com/user/updated",
  "is_public": false,
  "tag_ids": [1]
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Updated Title",
  "description": "Updated description",
  "github_url": "https://github.com/user/updated",
  "is_public": false,
  "owner_id": 1,
  "org_id": 1,
  "tags": [
    {"id": 1, "name": "Next.js"}
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**Errors**:
- `403 Forbidden`: Editor trying to update another user's project
- `404 Not Found`: Project doesn't exist

---

### Delete Project

Delete a project.

**Endpoint**: `DELETE /projects/{id}`

**Authentication**: Required

**RBAC**:
- Admin: Can delete any project
- Editor: Can only delete own projects
- Viewer: Cannot delete

**Response** (200 OK):
```json
{
  "message": "Project deleted successfully"
}
```

**Errors**:
- `403 Forbidden`: Editor trying to delete another user's project, or viewer trying to delete
- `404 Not Found`: Project doesn't exist

---

## Tags

### List Tags

Get all tags in the user's organization.

**Endpoint**: `GET /tags`

**Authentication**: Required (all roles)

**RBAC**: Admin, Editor, Viewer

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Next.js",
    "org_id": 1
  },
  {
    "id": 2,
    "name": "TypeScript",
    "org_id": 1
  }
]
```

---

### Create Tag

Create a new tag.

**Endpoint**: `POST /tags`

**Authentication**: Required

**RBAC**: Admin, Editor

**Request Body**:
```json
{
  "name": "React"
}
```

**Response** (200 OK):
```json
{
  "id": 3,
  "name": "React",
  "org_id": 1
}
```

**Errors**:
- `400 Bad Request`: Tag name already exists in organization
- `403 Forbidden`: Viewer trying to create tag

---

## Users

### List Users

Get all users in the organization (admin only).

**Endpoint**: `GET /users`

**Authentication**: Required

**RBAC**: Admin only

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "role": "admin",
    "org_id": 1,
    "created_at": "2024-01-15T10:00:00Z"
  },
  {
    "id": 2,
    "email": "editor@example.com",
    "role": "editor",
    "org_id": 1,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

**Errors**:
- `403 Forbidden`: Non-admin user attempting to access

---

### Create User

Create a new user in the organization (admin only).

**Endpoint**: `POST /users`

**Authentication**: Required

**RBAC**: Admin only

**Request Body**:
```json
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "role": "editor"
}
```

**Note**: Cannot create another admin user. Only "editor" or "viewer" roles allowed.

**Response** (200 OK):
```json
{
  "id": 3,
  "email": "newuser@example.com",
  "role": "editor",
  "org_id": 1,
  "created_at": "2024-01-15T12:00:00Z"
}
```

**Errors**:
- `400 Bad Request`: Email already exists, or trying to create admin role
- `403 Forbidden`: Non-admin user attempting to create user

---

### Get Current User

Get the currently authenticated user's information.

**Endpoint**: `GET /users/me`

**Authentication**: Required

**RBAC**: All roles

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "admin@example.com",
  "role": "admin",
  "org_id": 1,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## Activity Logs

### List Activity Logs

Get all activity logs for the organization (admin only).

**Endpoint**: `GET /activity`

**Authentication**: Required

**RBAC**: Admin only

**Query Parameters**:
- `skip` (optional): Offset for pagination (default: 0)
- `limit` (optional): Number of records to return (default: 100, max: 100)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "action": "CREATE",
    "entity": "project",
    "entity_id": 1,
    "actor_user_id": 1,
    "org_id": 1,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "action": "UPDATE",
    "entity": "project",
    "entity_id": 1,
    "actor_user_id": 2,
    "org_id": 1,
    "created_at": "2024-01-15T11:00:00Z"
  }
]
```

**Entity Types**:
- `project`
- `user`
- `tag`

**Action Types**:
- `CREATE`
- `UPDATE`
- `DELETE`

**Errors**:
- `403 Forbidden`: Non-admin user attempting to access

---

## Organizations

### Get Organization

Get the current user's organization information.

**Endpoint**: `GET /orgs/me`

**Authentication**: Required

**RBAC**: All roles

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "My Organization",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## Authentication Headers

All authenticated endpoints require the JWT access token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Example using curl:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://127.0.0.1:8000/projects
```

---

## Common Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

Causes:
- Missing Authorization header
- Invalid or expired access token
- Malformed token

**Solution**: Login again or refresh token

---

### 403 Forbidden
```json
{
  "detail": "Not authorized to perform this action"
}
```

Causes:
- User doesn't have required role (e.g., viewer trying to create project)
- Editor trying to modify another user's resource

**Solution**: Check RBAC requirements for endpoint

---

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

Causes:
- Resource doesn't exist
- Resource belongs to different organization

---

### 422 Unprocessable Entity
```json
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

Causes:
- Missing required fields
- Invalid field types
- Validation errors

**Solution**: Check request body format

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
  - Test endpoints directly in browser
  - See request/response schemas
  - Authenticate with JWT tokens

- **ReDoc**: http://127.0.0.1:8000/redoc
  - Alternative documentation interface
  - Better for reading and reference

---

## Rate Limiting

Currently, there is no rate limiting implemented. In production, consider:
- Rate limiting per IP address
- Rate limiting per user/API key
- Different limits for different roles

---

## Pagination

Activity logs support pagination via `skip` and `limit` query parameters.

Future enhancement: Add pagination to projects and tags endpoints for large datasets.

---

## Filtering and Sorting

Currently not implemented. Future enhancements:
- Filter projects by tag
- Filter projects by public/private
- Sort projects by creation date, title, etc.
- Filter activity logs by action type, entity type

---

## Example Workflows

### Complete User Journey

1. **Register Organization**
   ```bash
   POST /auth/register
   ```

2. **Login**
   ```bash
   POST /auth/login
   ```

3. **Create Tags**
   ```bash
   POST /tags (admin/editor)
   ```

4. **Create Project**
   ```bash
   POST /projects (admin/editor)
   ```

5. **View Projects**
   ```bash
   GET /projects (all roles)
   ```

6. **Update Project**
   ```bash
   PUT /projects/1 (admin or owner)
   ```

7. **View Activity Logs**
   ```bash
   GET /activity (admin only)
   ```

---

## API Versioning

Currently, the API is not versioned. All endpoints are at the root level.

Future: If breaking changes are needed, versioning would be added as `/v1/projects`, `/v2/projects`, etc.

---

## CORS Configuration

The API allows CORS requests from:
- `http://localhost:3000` (frontend development server)

In production, update `allow_origins` in `app/main.py` to include your production frontend domain.
