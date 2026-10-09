from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_list_and_get():
    assert len(client.get("/pois").json()) >= 2
    assert client.get("/pois/1").json()["id"] == 1


def test_not_found():
    assert client.get("/pois/999").status_code == 404


def test_create():
    r = client.post("/pois", json={"name": "Chợ Bến Thành", "description": "Chợ nổi tiếng."})
    assert r.status_code == 201
    assert client.get(f"/pois/{r.json()['id']}").status_code == 200
