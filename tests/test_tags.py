def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_tag(client):
    # Login as editor (created in test_rbac_and_project_crud)
    r = client.post("/auth/login", data={
        "username": "editor@rbac.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    editor_token = r.json()["access_token"]

    # Create a tag
    r = client.post("/tags", headers=auth_header(editor_token), json={
        "name": "Python",
    })
    assert r.status_code == 200, r.text
    tag = r.json()
    assert tag["name"] == "python"  # Should be lowercased
    assert tag["id"]


def test_list_tags(client):
    # Login as viewer
    r = client.post("/auth/login", data={
        "username": "viewer@rbac.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    viewer_token = r.json()["access_token"]

    # List tags
    r = client.get("/tags", headers=auth_header(viewer_token))
    assert r.status_code == 200
    tags = r.json()
    assert isinstance(tags, list)
    assert len(tags) >= 1  # At least the tags created in previous tests


def test_viewer_cannot_create_tag(client):
    # Login as viewer
    r = client.post("/auth/login", data={
        "username": "viewer@rbac.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200
    viewer_token = r.json()["access_token"]

    # Try to create a tag as viewer
    r = client.post("/tags", headers=auth_header(viewer_token), json={
        "name": "Forbidden Tag",
    })
    assert r.status_code == 403
