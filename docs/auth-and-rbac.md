# Authentication & RBAC

## Authentication Flow

### Registration Flow
1. User submits registration form with email, password, and organization name
2. Backend validates inputs (email format, password strength)
3. Password is hashed using Argon2
4. New organization is created
5. User is created as admin of that organization
6. User record stored in database with hashed password

### Login Flow
1. User submits login form via `/auth/login` (OAuth2 password flow)
2. Backend looks up user by email
3. Argon2 verifies password against stored hash
4. If valid:
   - Generate JWT access token (30 min expiry)
   - Generate JWT refresh token (7 days expiry)
   - Return both tokens plus user metadata
5. If invalid: Return `401 Unauthorized`

### Token Refresh Flow
1. Client detects expired access token (401 response)
2. Client sends refresh token to `/auth/refresh`
3. Backend validates refresh token signature and expiry
4. If valid:
   - Generate new access token
   - Generate new refresh token (refresh rotation)
   - Return both tokens
5. If invalid: Client must re-login

### Authenticated Request Flow
1. Client includes access token in `Authorization: Bearer <token>` header
2. FastAPI dependency extracts token
3. Backend verifies JWT signature and expiry
4. Backend extracts user identity from token payload
5. Backend loads user from database
6. User object is injected into route handler

---

## JWT Token Structure

### Access Token Payload
```json
{
  "sub": "user@example.com",      // Subject (user email)
  "org_id": 1,                     // Organization ID
  "role": "admin",                 // User role
  "user_id": 1,                    // User ID
  "exp": 1704567890,               // Expiration timestamp
  "type": "access"                 // Token type
}
```

### Refresh Token Payload
```json
{
  "sub": "user@example.com",       // Subject (user email)
  "exp": 1705172690,               // Expiration timestamp (7 days)
  "type": "refresh"                // Token type
}
```

### Token Security
- Tokens are signed with HS256 (HMAC SHA-256)
- Secret key stored in environment variable
- Tokens cannot be modified without invalidating signature
- Short expiry on access tokens limits compromise window
- Refresh tokens enable long sessions without storing state

**Note**: In production, consider:
- Token blacklist (Redis) for logout
- Store refresh tokens in httpOnly cookies (not localStorage)
- Add token fingerprinting to prevent token theft

---

## Password Security

### Argon2 Hashing

Passwords are hashed using **Argon2**, winner of the Password Hashing Competition.

**Implementation**:
```python
from argon2 import PasswordHasher

ph = PasswordHasher()

# On registration/password change
hashed_password = ph.hash("user_plain_password")

# On login
try:
    ph.verify(stored_hash, provided_password)
    # Password is correct
except argon2.exceptions.VerifyMismatchError:
    # Password is wrong
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

**Why Argon2:**
- Memory-hard (resistant to GPU/ASIC attacks)
- Configurable time, memory, and parallelism costs
- Better than bcrypt, PBKDF2, scrypt
- Recommended by OWASP

**Security Guarantees:**
- Plaintext passwords are **never** stored in database
- Plaintext passwords are **never** logged
- Password hashes are one-way (cannot be reversed)
- Same password hashes to different values each time (salt)

---

## Role-Based Access Control (RBAC)

### Supported Roles

- **admin**: Organization owner, full control
- **editor**: Content creator, limited administrative access
- **viewer**: Read-only user

**Role Assignment:**
- First user in organization is always admin (created at registration)
- Admin can create editor and viewer users
- Admin **cannot** create other admin users (security measure)
- Users cannot change their own role

### Permissions Matrix

| Feature | Action | Admin | Editor | Viewer |
|---------|--------|-------|--------|--------|
| **Authentication** | Login | ✅ | ✅ | ✅ |
| **Authentication** | Refresh token | ✅ | ✅ | ✅ |
| **Users** | List all users | ✅ | ❌ | ❌ |
| **Users** | Create user | ✅ | ❌ | ❌ |
| **Users** | View own profile | ✅ | ✅ | ✅ |
| **Projects** | List all projects | ✅ | ✅ | ✅ |
| **Projects** | View project | ✅ | ✅ | ✅ |
| **Projects** | Create project | ✅ | ✅ | ❌ |
| **Projects** | Update own project | ✅ | ✅ | ❌ |
| **Projects** | Update any project | ✅ | ❌ | ❌ |
| **Projects** | Delete own project | ✅ | ✅ | ❌ |
| **Projects** | Delete any project | ✅ | ❌ | ❌ |
| **Tags** | List all tags | ✅ | ✅ | ✅ |
| **Tags** | Create tag | ✅ | ✅ | ❌ |
| **Activity Logs** | View logs | ✅ | ❌ | ❌ |
| **Organization** | View org info | ✅ | ✅ | ✅ |

### Ownership Rules

**Project Ownership:**
- Creator of project is the owner
- Admin can modify/delete **any** project
- Editor can only modify/delete **own** projects
- Viewer cannot modify/delete any projects

**Example:**
```
User A (editor) creates Project 1 → User A owns Project 1
User B (editor) creates Project 2 → User B owns Project 2

User A can edit/delete Project 1 ✅
User A cannot edit/delete Project 2 ❌

User C (admin) can edit/delete both Project 1 and Project 2 ✅
```

---

## Enforcement Strategy

### Server-Side Enforcement

**Critical Principle**: RBAC is enforced **server-side only**, never trust the client.

### Implementation: Dependency Injection

FastAPI dependencies enforce authorization:

```python
# app/api/deps.py

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Extract and validate user from JWT token"""
    payload = decode_jwt(token)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401)
    return user

def get_current_user_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user has admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user

def require_admin_or_editor(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user has admin or editor role"""
    if current_user.role not in ["admin", "editor"]:
        raise HTTPException(
            status_code=403,
            detail="Editor or Admin access required"
        )
    return current_user
```

### Usage in Routes

```python
# Admin-only endpoint
@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_admin)
):
    # Only admins reach this code
    return db.query(User).filter(User.org_id == current_user.org_id).all()

# Admin or Editor endpoint
@router.post("/projects")
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_editor)
):
    # Viewers cannot reach this code (403 Forbidden)
    new_project = Project(**project.dict(), owner_id=current_user.id)
    db.add(new_project)
    db.commit()
    return new_project

# Custom ownership check
@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404)

    # Check permission: admin can delete any, editor can delete own
    if current_user.role == "admin":
        pass  # Admin can delete any project
    elif current_user.role == "editor" and project.owner_id == current_user.id:
        pass  # Editor can delete own project
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(project)
    db.commit()
    return {"message": "Deleted"}
```

### Why This Matters

1. **Prevents Privilege Escalation**
   - Cannot bypass frontend and call API directly
   - Cannot modify JWT token (signature verification)
   - Cannot access other organization's data

2. **Defense in Depth**
   - Frontend can hide buttons (UX improvement)
   - Backend always validates (security requirement)
   - Even if frontend is compromised, backend is safe

3. **Multi-Tenancy Isolation**
   - All queries scoped by `org_id`
   - Users can only access their organization's data
   - Even admin cannot access other organizations

---

## Security Best Practices Implemented

### ✅ What We Do

1. **Password Security**
   - Argon2 hashing (memory-hard)
   - No plaintext storage or logging
   - Salted hashes (unique per password)

2. **Token Security**
   - Short-lived access tokens (30 min)
   - Long-lived refresh tokens (7 days)
   - Signed with secret key (HS256)
   - Expiry validation on every request

3. **Authorization**
   - Server-side RBAC enforcement
   - Dependency injection for clean checks
   - Ownership validation (editor can only edit own)

4. **Multi-Tenancy**
   - All queries filter by `org_id`
   - Cross-organization access prevented
   - Database-level isolation

5. **Input Validation**
   - Pydantic schemas validate all inputs
   - SQL injection prevented by ORM
   - XSS prevented by JSON API

### ⚠️ Production Considerations

For a production deployment, consider adding:

1. **Token Revocation**
   - Redis-based token blacklist
   - Logout invalidates tokens
   - Session management

2. **Rate Limiting**
   - Prevent brute force login attempts
   - Per-user/IP rate limits
   - CAPTCHA after failed attempts

3. **2FA (Two-Factor Authentication)**
   - TOTP (Time-based One-Time Password)
   - SMS or email verification
   - Backup codes

4. **Account Security**
   - Password strength requirements
   - Password history (prevent reuse)
   - Account lockout after failed attempts
   - Email verification on registration

5. **Audit Logging**
   - Log all authentication attempts
   - Log all permission checks
   - Alert on suspicious activity

---

## Testing RBAC

RBAC is tested rigorously in `tests/test_rbac_projects.py`:

```python
def test_viewer_cannot_create_project(client, viewer_token_headers):
    """Verify viewers cannot create projects"""
    response = client.post(
        "/projects",
        json={"title": "Test", "description": "Test"},
        headers=viewer_token_headers
    )
    assert response.status_code == 403

def test_editor_cannot_delete_others_project(client, editor_token_headers, admin_token_headers):
    """Verify editors can only delete own projects"""
    # Admin creates a project
    admin_project = client.post(
        "/projects",
        json={"title": "Admin Project", "description": "Test"},
        headers=admin_token_headers
    ).json()

    # Editor tries to delete admin's project
    response = client.delete(
        f"/projects/{admin_project['id']}",
        headers=editor_token_headers
    )
    assert response.status_code == 403
```

**Coverage:**
- All role combinations tested
- Forbidden scenarios verified (403 responses)
- Ownership rules validated
- Cross-organization access blocked

---

## Common Security Questions

### Q: Why JWT instead of sessions?

**A**: Stateless authentication scales better:
- No server-side session storage needed
- Works well with load balancers and microservices
- Frontend and backend can be deployed separately

### Q: Why short-lived access tokens?

**A**: Limits damage if token is compromised:
- Stolen access token expires in 30 minutes
- Refresh token can be revoked if needed
- Balance between security and UX

### Q: Can users change their own role?

**A**: No, role is read-only:
- Only admins can create users with roles
- No endpoint to modify user role
- Role is validated server-side on every request

### Q: What if JWT secret key is compromised?

**A**: Rotate the secret key:
- All existing tokens become invalid
- Users must log in again
- Update environment variable and restart server

---

## Diagram: Authentication Flow

```
1. Registration
   User → POST /auth/register → [Validate] → [Hash Password] → [Create Org + Admin] → Database

2. Login
   User → POST /auth/login → [Verify Password] → [Generate JWT] → Access + Refresh Tokens

3. Authenticated Request
   User → GET /projects
        ↓ Headers: Authorization: Bearer <token>
        → [Extract Token] → [Verify Signature] → [Load User] → [Execute Route] → Response

4. Token Refresh
   User → POST /auth/refresh
        ↓ Body: {refresh_token}
        → [Verify Refresh Token] → [Generate New Tokens] → Access + Refresh Tokens
```

---

## Summary

**Authentication:**
- JWT-based, stateless
- Argon2 password hashing
- Access + refresh token pattern

**Authorization:**
- Role-based (admin, editor, viewer)
- Server-side enforcement
- Ownership validation

**Security:**
- Defense in depth
- Multi-tenancy isolation
- Comprehensive testing

This architecture ensures **secure, scalable authentication and authorization** suitable for production use.
