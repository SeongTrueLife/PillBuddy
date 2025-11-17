import base64

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from services import rag_service, tts_service, vision_service

app = FastAPI(title="PillBuddy Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    return {"message": "PillBuddy Backend is running!"}


@app.post("/api/v1/pills/identify")
async def identify_pill(file: UploadFile = File(...)):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="이미지 파일을 업로드해주세요.")

    pill_name = vision_service.identify_pill(contents)

    drug_info = rag_service.fetch_drug_info(pill_name)
    if drug_info:
        script = rag_service.generate_summary_with_rag(drug_info)
    else:
        # rag_service.generate_summary_backup이 존재한다고 가정합니다.
        script = rag_service.generate_summary_backup(pill_name)

    audio_bytes = tts_service.synthesize_speech(script)
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    else:
        audio_base64 = None

    return {
        "pill_name": pill_name,
        "script": script,
        "audio_base64": audio_base64,
    }

