from fastapi.testclient import TestClient

from app.main import app
from app.services.users import current_active_user
from app.database.models import UserModel

client = TestClient(app)


def test_translation(client_with_db: TestClient, verified_user: UserModel) -> None:
    # Authenticate the user
    app.dependency_overrides[current_active_user] = lambda: verified_user

    entities = [{"text": "quadri r/v", "entity": "IMPRESSION"}]
    model = "imprimeur"

    response = client.post("/translate", json={"entities": entities, "model": model})

    assert response.json() == {
        "entities": [
            {
                "text": "recto : quadri, verso : quadri",
                "entity": "IMPRESSION",
            }
        ]
    }
    assert response.status_code == 200
