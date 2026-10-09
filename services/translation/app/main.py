"""Translation Service: dịch văn bản sang ngôn ngữ đích."""
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Translation Service")
PROVIDER = os.getenv("TRANSLATE_PROVIDER", "mock")  # google | mock


class TranslateIn(BaseModel):
    text: str
    source: str = "vi"
    target: str


def translate_text(text: str, source: str, target: str) -> str:
    if source == target:
        return text
    if PROVIDER == "google":
        from deep_translator import GoogleTranslator

        return GoogleTranslator(source=source, target=target).translate(text)
    return f"[{target}] {text}"  # mock: dùng cho test/CI, không cần internet


@app.get("/health")
def health():
    return {"status": "ok", "service": "translation", "provider": PROVIDER}


@app.post("/translate")
def translate(body: TranslateIn):
    try:
        return {"translated_text": translate_text(body.text, body.source, body.target), "target": body.target}
    except Exception as exc:  # lỗi từ nhà cung cấp dịch
        raise HTTPException(502, f"Translation failed: {exc}")
