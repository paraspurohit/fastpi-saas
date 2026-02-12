def test_access_protected_without_token(client):
    res = client.get("/users/all")
    assert res.status_code == 401


def test_invalid_token_access(client):
    res = client.get("/users/all", headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401


def test_sql_injection_login(client):
    res = client.post(
        "/login/", data={"username": "' OR 1=1 --", "password": "anything"}
    )
    assert res.status_code in (400, 401)


def test_sql_injection_user_lookup(client):
    res = client.get("/users/' OR 1=1 --")
    assert res.status_code in (401, 400, 404)


def test_update_user_without_auth(client):
    res = client.put(
        "/users/update-detail", json={"first_name": "Hacker", "last_name": "Attack"}
    )
    assert res.status_code == 401


def test_delete_user_without_auth(client):
    res = client.delete("/users/delete/1")
    assert res.status_code == 401
