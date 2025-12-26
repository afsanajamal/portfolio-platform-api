def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_get_activity_logs_as_admin(client):
    # Register admin user
    r = client.post("/auth/register", json={
        "org_name": "Admin Test Org",
        "email": "admin_activity@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    admin_token = r.json()["access_token"]

    # Create editor to test permission
    r = client.post("/users", headers=auth_header(admin_token), json={
        "email": "editor_activity@test.com",
        "password": "strongpass123",
        "role": "editor",
    })
    assert r.status_code == 200

    # Get activity logs
    r = client.get("/activity", headers=auth_header(admin_token))
    assert r.status_code == 200
    activities = r.json()
    assert isinstance(activities, list)
    # Should have activities from previous tests (user creation, project creation, etc.)
    assert len(activities) > 0


def test_get_activity_logs_forbidden_for_non_admin(client):
    # Register admin and create editor
    r = client.post("/auth/register", json={
        "org_name": "Forbidden Test Org",
        "email": "admin_forbidden@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    admin_token = r.json()["access_token"]

    # Admin creates editor
    r = client.post("/users", headers=auth_header(admin_token), json={
        "email": "editor_forbidden@test.com",
        "password": "strongpass123",
        "role": "editor",
    })
    assert r.status_code == 200

    # Login as editor
    r = client.post("/auth/login", data={
        "username": "editor_forbidden@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    editor_token = r.json()["access_token"]

    # Try to get activity logs as editor
    r = client.get("/activity", headers=auth_header(editor_token))
    assert r.status_code == 403


def test_list_users_as_admin(client):
    # Register admin user
    r = client.post("/auth/register", json={
        "org_name": "Users List Org",
        "email": "admin_users@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    admin_token = r.json()["access_token"]

    # Admin creates some users
    r = client.post("/users", headers=auth_header(admin_token), json={
        "email": "user1@test.com",
        "password": "strongpass123",
        "role": "editor",
    })
    assert r.status_code == 200

    r = client.post("/users", headers=auth_header(admin_token), json={
        "email": "user2@test.com",
        "password": "strongpass123",
        "role": "viewer",
    })
    assert r.status_code == 200

    # List users in the organization
    r = client.get("/users", headers=auth_header(admin_token))
    assert r.status_code == 200
    users = r.json()
    assert isinstance(users, list)
    # Should have at least 3 users: admin, user1, user2
    assert len(users) >= 3


def test_list_users_forbidden_for_non_admin(client):
    # Register admin and create viewer
    r = client.post("/auth/register", json={
        "org_name": "Viewer Test Org",
        "email": "admin_viewer@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    admin_token = r.json()["access_token"]

    # Admin creates viewer
    r = client.post("/users", headers=auth_header(admin_token), json={
        "email": "viewer_test@test.com",
        "password": "strongpass123",
        "role": "viewer",
    })
    assert r.status_code == 200

    # Login as viewer
    r = client.post("/auth/login", data={
        "username": "viewer_test@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    viewer_token = r.json()["access_token"]

    # Try to list users as viewer
    r = client.get("/users", headers=auth_header(viewer_token))
    assert r.status_code == 403


def test_get_current_org(client):
    # Register a user
    r = client.post("/auth/register", json={
        "org_name": "Current Org Test",
        "email": "user_org@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    token = r.json()["access_token"]

    # Get current organization
    r = client.get("/orgs/me", headers=auth_header(token))
    assert r.status_code == 200
    org = r.json()
    assert org["name"] == "Current Org Test"
    assert org["id"]
