def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_new_user(client):
    response = client.post("/auth/register", json={"username": "juanp", "password": "clave123"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "juanp"
    assert data["role"] == "usuario"


def test_register_duplicate_username(client):
    client.post("/auth/register", json={"username": "juanp", "password": "clave123"})
    response = client.post("/auth/register", json={"username": "juanp", "password": "otraClave1"})
    assert response.status_code == 400


def test_register_password_too_short(client):
    response = client.post("/auth/register", json={"username": "juanp", "password": "123"})
    assert response.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json={"username": "juanp", "password": "clave123"})
    response = client.post("/auth/login", data={"username": "juanp", "password": "clave123"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "juanp", "password": "clave123"})
    response = client.post("/auth/login", data={"username": "juanp", "password": "incorrecta"})
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={"username": "nadie", "password": "clave123"})
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_valid_token(client, user_token):
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "user1"


def test_me_with_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer token-invalido"})
    assert response.status_code == 401


def test_admin_role_assigned_correctly(client, admin_token):
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["role"] == "admin"
