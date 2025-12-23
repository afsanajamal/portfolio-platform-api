# Authentication & RBAC

## Authentication Flow

1. User registers or is created by an admin
2. User logs in via `/auth/login`
3. Credentials are validated
4. JWT access & refresh tokens are issued
5. Client sends token in `Authorization: Bearer <token>`
6. Backend authenticates the request

---

## JWT

- Stateless authentication
- Signed using a secret key
- Contains user identity and role information
- No server-side session storage

---

## Password Security

Passwords are hashed using **Argon2**, a modern and secure hashing algorithm.

Plaintext passwords are never stored or logged.

---

## Role-Based Access Control (RBAC)

Roles supported:
- **admin**
- **editor**
- **viewer**

### Permissions

| Action | Admin | Editor | Viewer |
|------|------|------|------|
| Create users | ✅ | ❌ | ❌ |
| Create projects | ✅ | ✅ | ❌ |
| View projects | ✅ | ✅ | ✅ |
| View activity logs | ✅ | ❌ | ❌ |

RBAC is enforced **server-side**, not in the frontend.

---

## Enforcement Strategy

- User identity is extracted from JWT
- Role checks are applied inside route logic
- Unauthorized access returns `403 Forbidden`

This prevents privilege escalation even if a frontend is bypassed.
