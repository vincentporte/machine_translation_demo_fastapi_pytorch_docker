from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_jwt_register_and_auth(client_with_db: TestClient) -> None:

    email = "user@domain.com"
    password = "bépo"

    response = client.post(
        "/auth/register", json={"email": email, "password": password}
    )

    assert response.json()["email"] == "user@domain.com"
    assert response.json()["is_active"]
    assert not response.json()["is_superuser"]
    assert response.status_code == 201

    response = client.post(
        "/auth/login", data={"username": email, "password": password}
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


def test_jwt_register_and_failed_auth(client_with_db: TestClient) -> None:

    email = "user@domain.com"
    bad_password = "azerty"

    response = client.post(
        "/auth/login", data={"username": email, "password": bad_password}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "LOGIN_BAD_CREDENTIALS"}
