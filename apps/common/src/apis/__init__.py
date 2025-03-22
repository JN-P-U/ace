from apis.stt import root_router, stt_router
from fastapi import FastAPI

app = FastAPI(
    title="Common Server API",
    description="Azure STT 연동 기능을 포함한 API",
    version="1.0.0",
)

app.include_router(root_router)
app.include_router(stt_router)
