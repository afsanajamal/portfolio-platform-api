def test_register_login_refresh(client):
    r = client.post("/auth/register", json={
        "org_name": "Test Org",
        "email": "admin@test.com",
        "password": "strongpass123",
    })
    assert r.status_code == 200, r.text
    tokens = r.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    r2 = client.post("/auth/login", 
        data={
        "username": "admin@test.com",
        "password": "strongpass123",
    },)
    assert r2.status_code == 200, r2.text
    tokens2 = r2.json()

    r3 = client.post("/auth/refresh", json={"refresh_token": tokens2["refresh_token"]})
    assert r3.status_code == 200, r3.text
    tokens3 = r3.json()
    assert tokens3["access_token"]
    assert tokens3["refresh_token"]
