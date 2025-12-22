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
