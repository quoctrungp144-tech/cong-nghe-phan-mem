from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["service"] == "translation"


def test_translate_mock():
    r = client.post("/translate", json={"text": "Xin chào", "target": "en"})
    assert r.status_code == 200
    assert r.json()["translated_text"] == "[en] Xin chào"


def test_same_language_returns_original():
    r = client.post("/translate", json={"text": "Xin chào", "source": "vi", "target": "vi"})
    assert r.json()["translated_text"] == "Xin chào"
