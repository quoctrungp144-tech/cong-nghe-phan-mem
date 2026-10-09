"""Content Service: quản lý địa điểm (POI) và nội dung thuyết minh gốc (tiếng Việt)."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Content Service")


class POIIn(BaseModel):
    name: str
    description: str
    source_lang: str = "vi"


POIS: dict[int, dict] = {
    1: {
        "id": 1,
        "name": "Dinh Độc Lập",
        "description": "Dinh Độc Lập là nơi ghi dấu sự kiện thống nhất đất nước vào ngày 30 tháng 4 năm 1975.",
        "source_lang": "vi",
    },
    2: {
        "id": 2,
        "name": "Nhà thờ Đức Bà",
        "description": "Nhà thờ Đức Bà Sài Gòn được xây dựng từ năm 1863 đến năm 1880 với gạch đỏ nhập từ Pháp.",
        "source_lang": "vi",
    },
}


@app.get("/health")
def health():
    return {"status": "ok", "service": "content"}


@app.get("/pois")
def list_pois():
    return list(POIS.values())


@app.get("/pois/{poi_id}")
def get_poi(poi_id: int):
    if poi_id not in POIS:
        raise HTTPException(404, "POI not found")
    return POIS[poi_id]


@app.post("/pois", status_code=201)
def create_poi(poi: POIIn):
    new_id = max(POIS, default=0) + 1
    POIS[new_id] = {"id": new_id, **poi.model_dump()}
    return POIS[new_id]
