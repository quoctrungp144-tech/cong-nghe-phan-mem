"""API Gateway: điểm vào duy nhất, điều phối Content -> Translation -> TTS."""
import os

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

app = FastAPI(title="Narration Gateway")

CONTENT_URL = os.getenv("CONTENT_URL", "http://localhost:8001")
TRANSLATION_URL = os.getenv("TRANSLATION_URL", "http://localhost:8002")
TTS_URL = os.getenv("TTS_URL", "http://localhost:8003")
SUPPORTED_LANGS = {"vi", "en", "fr", "ja", "ko", "zh-CN"}
TIMEOUT = httpx.Timeout(30.0)


async def call_service(method: str, url: str, **kwargs) -> httpx.Response:
    """Gọi service khác qua HTTP; lỗi kết nối -> 502, service trả lỗi -> chuyển tiếp mã lỗi."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.request(method, url, **kwargs)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Cannot reach {url}: {exc}")
    if resp.status_code >= 400:
        raise HTTPException(resp.status_code if resp.status_code == 404 else 502, f"Upstream error from {url}")
    return resp


@app.get("/health")
async def health():
    status = {}
    for name, url in {"content": CONTENT_URL, "translation": TRANSLATION_URL, "tts": TTS_URL}.items():
        try:
            await call_service("GET", f"{url}/health")
            status[name] = "up"
        except HTTPException:
            status[name] = "down"
    return {"gateway": "ok", "services": status}


@app.get("/api/pois")
async def list_pois():
    return (await call_service("GET", f"{CONTENT_URL}/pois")).json()


@app.get("/api/narration/{poi_id}")
async def narration(poi_id: int, lang: str = Query("en")):
    if lang not in SUPPORTED_LANGS:
        raise HTTPException(400, f"Unsupported language. Choose from: {sorted(SUPPORTED_LANGS)}")

    poi = (await call_service("GET", f"{CONTENT_URL}/pois/{poi_id}")).json()

    tr = await call_service(
        "POST",
        f"{TRANSLATION_URL}/translate",
        json={"text": poi["description"], "source": poi["source_lang"], "target": lang},
    )
    text = tr.json()["translated_text"]

    tts = await call_service("POST", f"{TTS_URL}/synthesize", json={"text": text, "lang": lang})
    audio_id = tts.json()["audio_id"]

    return {
        "poi_id": poi_id,
        "name": poi["name"],
        "lang": lang,
        "text": text,
        "audio_url": f"/api/audio/{audio_id}",
    }


@app.get("/api/audio/{audio_id}")
async def audio(audio_id: str):
    resp = await call_service("GET", f"{TTS_URL}/audio/{audio_id}")
    return Response(content=resp.content, media_type=resp.headers.get("content-type", "audio/mpeg"))
