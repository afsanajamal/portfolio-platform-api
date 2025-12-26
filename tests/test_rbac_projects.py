def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def test_rbac_and_project_crud(client):
    reg = client.post("/auth/register", json={
        "org_name": "RBAC Org",
        "email": "admin@rbac.com",
        "password": "strongpass123",
    })
    assert reg.status_code == 200, reg.text
    admin_access = reg.json()["access_token"]

    # admin creates editor
    r = client.post("/users", headers=auth_header(admin_access), json={
        "email": "editor@rbac.com",
        "password": "strongpass123",
        "role": "editor",
    })
    assert r.status_code == 200, r.text

    # admin creates viewer
    r = client.post("/users", headers=auth_header(admin_access), json={
        "email": "viewer@rbac.com",
        "password": "strongpass123",
        "role": "viewer",
    })
    assert r.status_code == 200, r.text

    editor_access = client.post("/auth/login",
        data={
            "username": "editor@rbac.com",
            "password": "strongpass123",
        },
    ).json()["access_token"]
    viewer_access = client.post("/auth/login",
        data={
            "username": "viewer@rbac.com",
            "password": "strongpass123",
        },
    ).json()["access_token"]

    # editor creates project
    p = client.post("/projects", headers=auth_header(editor_access), json={
        "title": "Backend Project",
        "description": "FastAPI + Postgres",
        "is_public": True,
        "tag_names": ["fastapi", "postgres"],
    })
    assert p.status_code == 200, p.text
    pid = p.json()["id"]

    # viewer cannot create
    p2 = client.post("/projects", headers=auth_header(viewer_access), json={
        "title": "Nope",
        "description": "fail",
    })
    assert p2.status_code == 403

    # viewer can list
    lst = client.get("/projects", headers=auth_header(viewer_access))
    assert lst.status_code == 200
    assert len(lst.json()) >= 1

    # editor updates
    up = client.patch(f"/projects/{pid}", headers=auth_header(editor_access), json={"title":"Updated"})
    assert up.status_code == 200
    assert up.json()["title"] == "Updated"
    
    
    
def test_viewer_cannot_create_project(client):
    # login as viewer
    r = client.post(
        "/auth/login",
        data={
            "username": "viewer@rbac.com",
            "password": "strongpass123",
        },
    )
    assert r.status_code == 200
    viewer_token = r.json()["access_token"]

    # viewer tries to create a project
    r = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={
            "title": "Viewer Forbidden Project",
            "description": "This should not be allowed",
            "github_url": "https://github.com/example/repo",
            "is_public": True,
            "tag_names": [],
        },
    )

    assert r.status_code == 403
    
    
def test_list_projects_requires_auth(client):
    r = client.get("/projects")
    assert r.status_code == 401


def test_list_projects_as_editor(client):
    # login as editor created in test_rbac_and_project_crud
    r = client.post(
        "/auth/login",
        data={"username": "editor@rbac.com", "password": "strongpass123"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get("/projects", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_delete_project(client):
    # Login as editor
    r = client.post("/auth/login", data={
        "username": "editor@rbac.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    editor_token = r.json()["access_token"]

    # Create a project to delete
    r = client.post("/projects", headers=auth_header(editor_token), json={
        "title": "Project to Delete",
        "description": "This project will be deleted",
    })
    assert r.status_code == 200
    project_id = r.json()["id"]

    # Delete the project
    r = client.delete(f"/projects/{project_id}", headers=auth_header(editor_token))
    assert r.status_code == 200
    assert r.json()["ok"] is True

    # Verify project is deleted (404 when trying to access it)
    r = client.patch(f"/projects/{project_id}", headers=auth_header(editor_token), json={
        "title": "Should not work",
    })
    assert r.status_code == 404

