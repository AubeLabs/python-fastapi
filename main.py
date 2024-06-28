from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from typing import Any

app = FastAPI()
# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 허용할 출처 리스트 (예: ["http://example.com"])
    allow_credentials=True,
    allow_methods=["*"],  # 허용할 HTTP 메서드 리스트 (예: ["GET", "POST"])
    allow_headers=["*"],  # 허용할 HTTP 헤더 리스트 (예: ["Authorization", "Content-Type"])
)

SEOUL_API_URL = "http://openapi.seoul.go.kr:8088/{api_key}/json/bikeList/1/10/"
SEOUL_API_KEY = "61616c5a67617562343345756e4279"  # 서울시 공공데이터 API 키
SEOUL_BIKE_API_URL = os.getenv("SEOUL_BIKE_API_URL")
SEOUL_BIKE_API_KEY = os.getenv("SEOUL_BIKE_API_KEY")

NEIS_API_KEY = "a022005bb22b49449d528d515d983b98"   # 나이스 교육정보 개방 포털 API 키
NEIS_API_URL = "https://open.neis.go.kr/hub/elsTimetable?KEY={api_key}&Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7021105&AY=2024&GRADE=2&CLASS_NM=2&TI_FROM_YMD=20240614&TI_TO_YMD=20240614"
NEIS_ELS_TIMETABLE_API_URL = "https://open.neis.go.kr/hub/elsTimetable?KEY={api_key}&Type=json&pIndex=1&pSize=100"
NEIS_ELS_MEALSERVICE_API_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={api_key}&Type=json&pIndex=1&pSize=100"

@app.get("/")
def read_root():
    return {"Rest API": "Aube Labs."}

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

@app.get("/api/bike-stations/{station_id}")
def get_bike_station(station_id: str):
    """
    서울시 공공데이터 API에서 자전거 대여소 정보를 가져옵니다.
    station_id를 경로 변수로 받아서 해당 대여소 정보를 반환합니다.
    """
    try:
        response = requests.get(
            f"{SEOUL_BIKE_API_URL}",
            params={"stationId": station_id, "api_key": SEOUL_BIKE_API_KEY}
        )
        response.raise_for_status()
        data = response.json()
        # API의 실제 응답 구조에 따라 data 가공 필요
        if not data:
            raise HTTPException(status_code=404, detail="Station not found")
        return data
    except requests.HTTPError as exc:
        raise HTTPException(status_code=response.status_code, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/els-timetables")
def get_els_timetables() -> Any:
    """
    초등학교시간표 정보를 가져와 리턴하는 API 엔드포인트.
    ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7021105&AY=2024&GRADE=2&CLASS_NM=2&TI_FROM_YMD=20240614&TI_TO_YMD=20240614
    """
    response = requests.get(NEIS_API_URL.format(api_key=NEIS_API_KEY))

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {"error": "Failed to retrieve data", "status_code": response.status_code}

@app.get("/api/els-timetable/{atpt_ofcdc_sc_code}/{sd_schul_code}/{ay}/{grade}/{class_nm}/{ti_ymd}")
def get_els_timetable(atpt_ofcdc_sc_code: str, sd_schul_code: str, ay: str, grade: str, class_nm: str, ti_ymd: str):
    """
    초등학교시간표 정보를 가져와 리턴하는 API 엔드포인트.
    ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7021105&AY=2024&GRADE=2&CLASS_NM=2&TI_FROM_YMD=20240614&TI_TO_YMD=20240614
    """
    try:
        response = requests.get(
            f"{NEIS_ELS_TIMETABLE_API_URL.format(api_key=NEIS_API_KEY)}",
            params={
                "ATPT_OFCDC_SC_CODE": atpt_ofcdc_sc_code
                , "SD_SCHUL_CODE": sd_schul_code
                , "AY": ay
                , "GRADE": grade
                , "CLASS_NM": class_nm
                , "TI_FROM_YMD": ti_ymd
                , "TI_TO_YMD": ti_ymd
            }
        )
        response.raise_for_status()
        data = response.json()
        # API의 실제 응답 구조에 따라 data 가공 필요
        if not data:
            raise HTTPException(status_code=404, detail="Timetable not found")
        return data
    except requests.HTTPError as exc:
        raise HTTPException(status_code=response.status_code, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/els-mealservice/{atpt_ofcdc_sc_code}/{sd_schul_code}/{meal_sc_code}/{ti_ymd}")
def get_els_mealservice(atpt_ofcdc_sc_code: str, sd_schul_code: str, meal_sc_code: str, ti_ymd: str):
    """
    급식식단정보를 가져와 리턴하는 API 엔드포인트.
    """
    try:
        response = requests.get(
            f"{NEIS_ELS_MEALSERVICE_API_URL.format(api_key=NEIS_API_KEY)}",
            params={
                "ATPT_OFCDC_SC_CODE": atpt_ofcdc_sc_code
                , "SD_SCHUL_CODE": sd_schul_code
                , "MMEAL_SC_CODE": meal_sc_code
                , "MLSV_YMD": ti_ymd
                , "MLSV_FROM_YMD": ti_ymd
                , "MLSV_TO_YMD": ti_ymd
            }
        )
        response.raise_for_status()
        data = response.json()
        # API의 실제 응답 구조에 따라 data 가공 필요
        if not data:
            raise HTTPException(status_code=404, detail="Timetable not found")
        return data
    except requests.HTTPError as exc:
        raise HTTPException(status_code=response.status_code, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
