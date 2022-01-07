from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_status(client: TestClient):
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"msg": "status up"}


def test_home(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "msg": f"wercome on our character level sequence 2 sequence machine translation demo"
    }
