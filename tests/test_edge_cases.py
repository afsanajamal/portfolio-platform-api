def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_register_with_invalid_email(client):
    # Try to register with invalid email format
    r = client.post("/auth/register", json={
        "org_name": "Invalid Org",
        "email": "not-an-email",
        "password": "strongpass123",
    })
    assert r.status_code == 422  # Validation error


def test_create_project_with_invalid_data(client):
    # Register admin and create editor
    r = client.post("/auth/register", json={
        "org_name": "Invalid Data Test Org",
        "email": "admin_invalid@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    admin_token = r.json()["access_token"]

    # Create editor
    r = client.post("/users", headers=auth_header(admin_token), json={
        "email": "editor_invalid@test.com",
        "password": "strongpass123",
        "role": "editor",
    })
    assert r.status_code == 200

    # Login as editor
    r = client.post("/auth/login", data={
        "username": "editor_invalid@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    editor_token = r.json()["access_token"]

    # Try to create project with title too short (min_length=2)
    r = client.post("/projects", headers=auth_header(editor_token), json={
        "title": "A",  # Too short
        "description": "Test description",
    })
    assert r.status_code == 422  # Validation error

    # Try to create project without required description
    r = client.post("/projects", headers=auth_header(editor_token), json={
        "title": "Valid Title",
        # Missing description
    })
    assert r.status_code == 422  # Validation error


def test_register_duplicate_email(client):
    # Register first user
    r = client.post("/auth/register", json={
        "org_name": "Duplicate Test Org",
        "email": "duplicate@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200

    # Try to register with same email
    r = client.post("/auth/register", json={
        "org_name": "Another Org",
        "email": "duplicate@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 409  # Conflict - email already exists


def test_invalid_token(client):
    # Use a completely invalid token
    fake_token = "this-is-not-a-valid-jwt-token"

    # Try to access protected endpoint with invalid token
    r = client.get("/projects", headers=auth_header(fake_token))
    assert r.status_code == 401  # Unauthorized


def test_expired_token(client):
    # Use a malformed JWT token (simulates expired/invalid token)
    malformed_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    # Try to access protected endpoint with malformed token
    r = client.get("/projects", headers=auth_header(malformed_token))
    assert r.status_code == 401  # Unauthorized


def test_cross_org_project_access(client):
    # Create first organization and user
    r = client.post("/auth/register", json={
        "org_name": "Org A",
        "email": "user_a@org.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    org_a_token = r.json()["access_token"]

    # Create a project in Org A
    r = client.post("/projects", headers=auth_header(org_a_token), json={
        "title": "Org A Project",
        "description": "This belongs to Org A",
    })
    assert r.status_code == 200
    org_a_project_id = r.json()["id"]

    # Create second organization and user
    r = client.post("/auth/register", json={
        "org_name": "Org B",
        "email": "user_b@org.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    org_b_token = r.json()["access_token"]

    # User from Org B tries to access Org A's project
    r = client.patch(
        f"/projects/{org_a_project_id}",
        headers=auth_header(org_b_token),
        json={"title": "Trying to update cross-org"},
    )
    assert r.status_code == 404  # Not found (because it's filtered by org_id)

    # User from Org B tries to delete Org A's project
    r = client.delete(
        f"/projects/{org_a_project_id}",
        headers=auth_header(org_b_token),
    )
    assert r.status_code == 404  # Not found (because it's filtered by org_id)
