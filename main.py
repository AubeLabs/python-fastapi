from fastapi import FastAPI
import requests
from typing import Any

app = FastAPI()

SEOUL_API_URL = "http://openapi.seoul.go.kr:8088/{api_key}/json/bikeList/1/10/"
SEOUL_API_KEY = "61616c5a67617562343345756e4279"  # 서울시 공공데이터 API 키

@app.get("/api/bike-stations")
def get_bike_stations() -> Any:
    """
    서울시 공공 자전거 대여소 정보를 가져와 리턴하는 API 엔드포인트.
    """
    response = requests.get(SEOUL_API_URL.format(api_key=SEOUL_API_KEY))

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {"error": "Failed to retrieve data", "status_code": response.status_code}
