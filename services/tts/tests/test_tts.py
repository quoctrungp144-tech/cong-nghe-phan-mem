from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_synthesize_and_download():
    r = client.post("/synthesize", json={"text": "hello", "lang": "en"})
    assert r.status_code == 201
    audio_id = r.json()["audio_id"]
    assert client.get(f"/audio/{audio_id}").status_code == 200


def test_audio_not_found():
    assert client.get("/audio/khong-ton-tai.wav").status_code == 404
