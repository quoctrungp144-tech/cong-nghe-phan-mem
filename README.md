# Thuyết minh tự động đa ngôn ngữ – Phần 3: Backend Services + CI/CD

Các service backend giao tiếp với nhau qua HTTP/REST, có CI/CD bằng GitHub Actions.

## Kiến trúc

```
Client ──> Gateway (:8000) ──> Content Service      (lấy nội dung gốc tiếng Việt)
                          ├──> Translation Service  (dịch sang ngôn ngữ đích)
                          └──> TTS Service          (chuyển văn bản thành giọng đọc)
```

| Service | Vai trò | Endpoint chính |
|---|---|---|
| gateway | Cổng vào duy nhất, điều phối các service | `GET /api/pois`, `GET /api/narration/{id}?lang=en`, `GET /api/audio/{audio_id}` |
| content | Quản lý địa điểm (POI) & nội dung gốc | `GET/POST /pois`, `GET /pois/{id}` |
| translation | Dịch văn bản | `POST /translate` |
| tts | Tạo file âm thanh | `POST /synthesize`, `GET /audio/{id}` |

Ngôn ngữ hỗ trợ: `vi, en, fr, ja, ko, zh-CN`. Mỗi service có `/health`.

## Chạy bằng Docker

```bash
docker compose up --build
# Dùng provider giả (không cần internet):
TRANSLATE_PROVIDER=mock TTS_PROVIDER=mock docker compose up --build
```

Thử:
```bash
curl http://localhost:8000/api/pois
curl "http://localhost:8000/api/narration/1?lang=en"
# -> {"text": "...", "audio_url": "/api/audio/xxxx.mp3"}
```
Swagger UI của gateway: http://localhost:8000/docs

## Chạy test

```bash
pip install -r requirements-dev.txt
cd services/content && pip install -r requirements.txt && pytest
```
(Làm tương tự cho gateway, translation, tts.)

## CI/CD

- **CI** (`.github/workflows/ci.yml`): chạy pytest cho từng service (matrix) + integration test bằng docker compose.
- **CD** (`.github/workflows/cd.yml`): khi push lên `main` hoặc tag `v*`, build & đẩy Docker image lên GitHub Container Registry (`ghcr.io/<owner>/narration-<service>`).

## Cấu trúc thư mục

```
.github/workflows/   # ci.yml, cd.yml
services/
  gateway/ content/ translation/ tts/   # mỗi service: app/, tests/, Dockerfile, requirements.txt
docker-compose.yml
```
