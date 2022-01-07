from fastapi.testclient import TestClient

from app.main import app
from app.services.users import current_active_user, current_active_verified_user
from app.database.models import UserModel

client = TestClient(app)


def test_create_and_collect_products(
    client_with_db: TestClient, verified_user: UserModel
) -> None:

    # TBC after solving this bug
    # https://github.com/tortoise/tortoise-orm/issues/1029

    # Authenticate the user
    app.dependency_overrides[current_active_user] = lambda: verified_user

    response = client_with_db.get("/products")
    assert response.json() == []
    assert response.status_code == 200


def test_patch_products(client_with_db: TestClient, verified_user: UserModel) -> None:
    assert True


def test_delete_products(client_with_db: TestClient, verified_user: UserModel) -> None:
    assert True


def test_bulk_post_products(
    client_with_db: TestClient, verified_user: UserModel
) -> None:
    assert True


def test_extract_unverified(
    client_with_db: TestClient, unverified_user: UserModel
) -> None:
    # Authenticate the user
    app.dependency_overrides[current_active_user] = lambda: unverified_user

    response = client_with_db.post("/products/extract")

    assert response.json() == {"detail": "Unauthorized"}
    assert response.status_code == 401


def test_extract_verified(client_with_db: TestClient, verified_user: UserModel) -> None:
    # Authenticate the user
    app.dependency_overrides[current_active_verified_user] = lambda: verified_user

    response = client_with_db.post("/products/extract")

    assert response.json() == {"msg": "extracting"}
    assert response.status_code == 200
