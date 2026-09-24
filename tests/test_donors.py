def test_create_donor_requires_auth(client):
    response = client.post(
        "/donors",
        json={
            "full_name": "Empresa X",
            "email": "contacto@empresax.com",
            "resource_type": "Alimentos enlatados",
        },
    )
    assert response.status_code == 401


def test_create_and_get_donor(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post(
        "/donors",
        json={
            "full_name": "Empresa X",
            "email": "contacto@empresax.com",
            "phone": "6671234567",
            "resource_type": "Alimentos enlatados",
        },
        headers=headers,
    )
    assert response.status_code == 201
    donor_id = response.json()["id"]

    get_response = client.get(f"/donors/{donor_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["full_name"] == "Empresa X"


def test_create_donor_invalid_email(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post(
        "/donors",
        json={
            "full_name": "Empresa X",
            "email": "no-es-un-correo",
            "resource_type": "Alimentos enlatados",
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_list_donors(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    client.post(
        "/donors",
        json={"full_name": "Empresa Y", "email": "y@empresa.com", "resource_type": "Ropa"},
        headers=headers,
    )
    response = client.get("/donors", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_nonexistent_donor(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/donors/9999", headers=headers)
    assert response.status_code == 404


def test_delete_donor_as_usuario_forbidden(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    create_resp = client.post(
        "/donors",
        json={"full_name": "Empresa Z", "email": "z@empresa.com", "resource_type": "Medicinas"},
        headers=headers,
    )
    donor_id = create_resp.json()["id"]

    response = client.delete(f"/donors/{donor_id}", headers=headers)
    assert response.status_code == 403


def test_delete_donor_as_admin(client, user_token, admin_token):
    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    create_resp = client.post(
        "/donors",
        json={"full_name": "Empresa W", "email": "w@empresa.com", "resource_type": "Agua"},
        headers=user_headers,
    )
    donor_id = create_resp.json()["id"]

    response = client.delete(f"/donors/{donor_id}", headers=admin_headers)
    assert response.status_code == 204

    get_resp = client.get(f"/donors/{donor_id}", headers=admin_headers)
    assert get_resp.status_code == 404


def test_delete_nonexistent_donor_as_admin(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete("/donors/9999", headers=headers)
    assert response.status_code == 404
