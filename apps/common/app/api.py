# apps/common/app/server.py
from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
from src.recognition.main import start_continuous_recognition, stop_continuous_recognition, stt_result_generator

app = FastAPI(
    title="Common Server API",
    description="Azure STT 연동 기능을 포함한 API",
    version="1.0.0"
)

# 기본(root) API 그룹
root_router = APIRouter(
    tags=["Root"]
)

@root_router.get("/", summary="헬스 체크")
def read_root():
    return {"message": "Common Server is running"}

# STT API 그룹
stt_router = APIRouter(
    prefix="/stt",
    tags=["STT"]
)

@stt_router.get("/start", summary="STT 인식 시작", description="Azure STT 인식을 시작합니다.", operation_id="start_stt")
def start_stt():

    # STT 세션 시작
    start_continuous_recognition()

    # 인식 결과 스트리밍 응답 (SSE)
    return StreamingResponse(stt_result_generator(), media_type="text/event-stream")

@stt_router.get("/stop", summary="STT 인식 종료", description="Azure STT 인식을 종료합니다.", operation_id="stop_stt")
def stop_stt():
    # STT 인식을 종료합니다.
    results = stop_continuous_recognition()
    return {"message": "Azure STT recognition stopped", "results": results}

app.include_router(root_router)
app.include_router(stt_router)