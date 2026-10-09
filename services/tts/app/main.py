"""TTS Service: chuyển văn bản thành giọng đọc (file âm thanh)."""
import math
import os
import struct
import uuid
import wave

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="TTS Service")
PROVIDER = os.getenv("TTS_PROVIDER", "mock")  # gtts | mock
AUDIO_DIR = os.getenv("AUDIO_DIR", "audio_files")
os.makedirs(AUDIO_DIR, exist_ok=True)


class SynthIn(BaseModel):
    text: str
    lang: str = "vi"


def _write_beep(path: str) -> None:
    """Mock: tạo file wav 0.3s để test mà không cần internet."""
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        frames = b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / 8000))) for i in range(2400))
        w.writeframes(frames)


@app.get("/health")
def health():
    return {"status": "ok", "service": "tts", "provider": PROVIDER}


@app.post("/synthesize", status_code=201)
def synthesize(body: SynthIn):
    ext = "mp3" if PROVIDER == "gtts" else "wav"
    audio_id = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(AUDIO_DIR, audio_id)
    try:
        if PROVIDER == "gtts":
            from gtts import gTTS

            gTTS(text=body.text, lang=body.lang.split("-")[0]).save(path)
        else:
            _write_beep(path)
    except Exception as exc:
        raise HTTPException(502, f"TTS failed: {exc}")
    return {"audio_id": audio_id, "lang": body.lang}


@app.get("/audio/{audio_id}")
def get_audio(audio_id: str):
    path = os.path.join(AUDIO_DIR, os.path.basename(audio_id))  # chống path traversal
    if not os.path.isfile(path):
        raise HTTPException(404, "Audio not found")
    return FileResponse(path)
