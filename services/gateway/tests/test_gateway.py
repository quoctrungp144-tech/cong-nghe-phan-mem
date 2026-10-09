import httpx
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def fake_response(status, json_data):
    return httpx.Response(status, json=json_data, request=httpx.Request("GET", "http://x"))


async def fake_call(method, url, **kwargs):
    if url.endswith("/pois/1"):
        return fake_response(200, {"id": 1, "name": "Dinh", "description": "Mô tả", "source_lang": "vi"})
    if url.endswith("/translate"):
        return fake_response(200, {"translated_text": "Description"})
    if url.endswith("/synthesize"):
        return fake_response(201, {"audio_id": "abc.mp3"})
    raise AssertionError(f"Unexpected call {url}")


def test_narration_orchestrates_services(monkeypatch):
    monkeypatch.setattr(main, "call_service", fake_call)
    r = client.get("/api/narration/1?lang=en")
    assert r.status_code == 200
    body = r.json()
    assert body["text"] == "Description"
    assert body["audio_url"] == "/api/audio/abc.mp3"


def test_unsupported_language():
    assert client.get("/api/narration/1?lang=xx").status_code == 400
