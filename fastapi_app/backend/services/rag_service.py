import os
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

E_YAK_API_KEY = os.getenv("E_YAK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not E_YAK_API_KEY:
    raise RuntimeError("E_YAK_API_KEY is not set in the environment.")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in the environment.")

API_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"

genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel("gemini-2.5-flash")


def fetch_drug_info(item_name: str) -> Optional[List[Dict[str, Any]]]:
    params = {
        "ServiceKey": E_YAK_API_KEY,
        "itemName": item_name,
        "type": "json",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "body" in data and data["body"].get("totalCount", 0) > 0:
            return data["body"]["items"]
        return None
    except requests.RequestException as exc:
        print(f"[rag_service] Drug info fetch failed: {exc}")
        return None


def generate_summary_with_rag(drug_data_json: List[Dict[str, Any]]) -> str:
    prompt = f"""
    당신은 시각장애인 환자를 돕는 '친절한 약사' AI입니다.

    [DB (e약은요 API 공식 데이터)]
    {drug_data_json}

    위 [DB]에만 100% 근거해서, 이 약의 '핵심 정보 4가지' (1. 약 이름, 2. 효능, 3. 사용법, 4. 핵심 주의 경고)를 
    '음성'으로 듣기 편하게, 매우 '친절한' 대화 말투로 요약해 주세요.

    마지막 문장은 반드시 "추가로 궁금한 점이 있으시면 화면을 터치한 뒤 말로 PillBuddy에게 질문해주세요."라는 문장으로 끝내 주세요.
    """

    try:
        response = MODEL.generate_content(prompt)
        return response.text
    except Exception as exc:
        print(f"[rag_service] Failed to generate RAG summary: {exc}")
        return "죄송합니다. 약물 정보를 요약하는 데 실패했습니다."


def generate_summary_backup(item_name: str) -> str:
    prompt = f"""
    당신은 시각장애인 환자를 돕는 '친절한 약사' AI입니다.
    'e약은요' 공식 DB에는 '{item_name}'의 정보가 없습니다.

    대신, 당신이 '일반적으로' 알고 있는 '{item_name}'에 대한 
    '핵심 정보 3가지' (1. 효능, 2. 사용법, 3. 주의 경고)를 
    '음성'으로 듣기 편하게, 매우 '친절한' 대화 말투로 요약해 주세요. 요약 설명 후 "공식 DB에 없는 내용이니 반드시 약사나 의사와 상담해주세요." 라는 문구를 추가해주세요.
    마지막 문장은 반드시 "추가로 궁금한 점이 있으시면 화면을 터치하고 말로 PillBuddy에게 질문해주세요."라는 문장으로 끝내 주세요.
    """

    try:
        response = MODEL.generate_content(prompt)
        return response.text
    except Exception as exc:
        print(f"[rag_service] Failed to generate backup summary: {exc}")
        return "죄송합니다. 약물 정보를 요약하는 데 실패했습니다."


def answer_follow_up_with_rag(user_question: str, rag_data_json: List[Dict[str, Any]]) -> str:
    prompt = f"""
    당신은 시각장애인 환자를 돕는 '친절한 약사' AI입니다.

    [교과서 (e약은요 API 공식 데이터)]
    {rag_data_json}

    [환자의 추가 질문]
    "{user_question}"

    위 [교과서]에만 100% 근거해서, 환자의 [추가 질문]에 대해 '친절한' 대화 말투로 답변해 주세요.
    [교과서]에 없는 말은 절대 지어내지 마세요.
    만약 [교과서]에서 답을 찾을 수 없다면, "그 부분은 [교과서]에 기재되어 있지 않아 정확한 답변이 어렵습니다. 의사나 약사와 상담해주세요."라고 말해주세요.
    """

    try:
        response = MODEL.generate_content(prompt)
        return response.text
    except Exception as exc:
        print(f"[rag_service] Failed to answer follow-up with RAG: {exc}")
        return "죄송합니다. 추가 질문에 답변하는 데 실패했습니다."


def answer_follow_up_backup(user_question: str, item_name: str) -> str:
    prompt = f"""
    당신은 시각장애인 환자를 돕는 '친절한 약사' AI입니다.
    'e약은요' 공식 DB에는 '{item_name}'의 정보가 없습니다.

    [환자의 추가 질문]
    "{user_question}"

    당신이 '일반적으로' 알고 있는 지식을 바탕으로, 환자의 [추가 질문]에 대해 '친절한' 대화 말투로 답변해 주세요.
    답변 마지막에는 "이 답변은 AI의 일반 지식에 기반한 참고용이며, 정확하지 않을 수 있으니 반드시 의사나 약사와 상담하세요."라는 문장을 포함해 주세요.
    """

    try:
        response = MODEL.generate_content(prompt)
        return response.text
    except Exception as exc:
        print(f"[rag_service] Failed to answer follow-up backup: {exc}")
        return "죄송합니다. 추가 질문에 답변하는 데 실패했습니다."


def answer_followup_question(pill_name: str, question: str) -> str:
    drug_info = fetch_drug_info(pill_name)
    if drug_info:
        context = drug_info
        prompt = f"""
        당신은 시각장애인 환자를 돕는 친절한 약사입니다.

        [약 정보]
        {context}

        사용자가 보고 있는 약은 "{pill_name}"입니다.
        사용자가 이렇게 질문했습니다: "{question}"

        위 약 정보에 최대한 근거해서 친절하게 답변해 주세요.
        만약 정보에 없는 내용이라면 "해당 정보는 현재 데이터에 없어 정확한 답을 드리기 어렵습니다. 의사나 약사와 상담해주세요."라고 안내하세요.
        마지막 문장은 반드시 "추가로 궁금한 점이 있으시면 화면을 터치한 뒤 말로 PillBuddy에게 질문해주세요."라는 문장으로 끝내 주세요.
        """
    else:
        prompt = f"""
        당신은 시각장애인 환자를 돕는 친절한 약사입니다.

        사용자가 보고 있는 약은 "{pill_name}"입니다.
        하지만 공식 데이터베이스에서 추가 정보를 찾지 못했습니다.
        사용자가 이렇게 질문했습니다: "{question}"

        당신이 일반적으로 알고 있는 지식을 바탕으로 답변하되,
        "이 답변은 일반 정보에 기반한 참고용이며 정확하지 않을 수 있으니 반드시 의사나 약사와 상담하세요."라는 문장을 반드시 덧붙여 주세요.
        마지막 문장은 반드시 "추가로 궁금한 점이 있으시면 화면을 터치한 뒤 말로 PillBuddy에게 질문해주세요."라는 문장으로 끝내 주세요.
        """

    try:
        response = MODEL.generate_content(prompt)
        return response.text
    except Exception as exc:
        print(f"[rag_service] Failed to answer followup question: {exc}")
        return "죄송합니다. 추가 질문에 답변하는 데 실패했습니다."

