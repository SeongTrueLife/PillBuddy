import base64
from typing import Dict

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services import rag_service, tts_service, vision_service

app = FastAPI(title="PillBuddy Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_storage: Dict[str, str] = {}


class FollowupRequest(BaseModel):
    session_id: str
    question: str


@app.get("/")
async def health_check():
    return {"message": "PillBuddy Backend is running!"}


@app.post("/api/v1/pills/identify")
async def identify_pill(
    session_id: str = Query(..., description="세션 식별자"),
    file: UploadFile = File(...),
):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="이미지 파일을 업로드해주세요.")

    pill_name = vision_service.identify_pill(contents)
    if not pill_name:
        raise HTTPException(status_code=422, detail="약을 식별하지 못했습니다. 다시 촬영해주세요.")

    drug_info = rag_service.fetch_drug_info(pill_name)
    if drug_info:
        script = rag_service.generate_summary_with_rag(drug_info)
    else:
        # rag_service.generate_summary_backup이 존재한다고 가정합니다.
        script = rag_service.generate_summary_backup(pill_name)

    session_storage[session_id] = pill_name

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


@app.post("/api/v1/pills/followup")
async def followup_question(payload: FollowupRequest):
    pill_name = session_storage.get(payload.session_id)
    if not pill_name:
        raise HTTPException(status_code=400, detail="먼저 약을 촬영해주세요.")

    answer = rag_service.answer_followup_question(pill_name, payload.question)
    audio_bytes = tts_service.synthesize_speech(answer)
    audio_base64 = (
        base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else None
    )

    return {
        "pill_name": pill_name,
        "question": payload.question,
        "answer": answer,
        "audio_base64": audio_base64,
    }

