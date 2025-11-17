# gemini_service.py

import google.generativeai as genai
import json
import config # 1. '금고'를 수입(import)한다!

# --- (열쇠를 '금고'에서 꺼내 쓰도록 수정!) ---
GEMINI_API_KEY = config.GEMINI_API_KEY # 2. '금고'에서 꺼내 씀

# '열쇠'로 Gemini 엔진 시동 걸기
genai.configure(api_key=GEMINI_API_KEY) # (이 부분은 config.GEMINI_API_KEY로 바꿔도 됨)


# 사용할 Gemini 모델 설정 (제일 똘똘한 녀석)
model = genai.GenerativeModel('gemini-2.5-flash')


# --- 이게 '메인 공장(app.py)'이 호출할 '부품 1 (Plan A 엔진)' ---
def generate_summary_with_rag(drug_data_json):
    """
    Plan A: 'e약은요'가 준 'JSON 덩어리(교과서)'를 받아서,
    '친절한 대화' 스크립트를 생성합니다.
    """
    
    print(f"[부품 2호 / Plan A] 'e약은요' 데이터를 기반으로 '대본' 생성 요청...")
    
    # Gemini한테 보낼 '명령서 (프롬프트)'
    prompt = f"""
    당신은 시각장애인 환자를 돕는 '친절한 약사' AI입니다.
    
    [교과서 (e약은요 API 공식 데이터)]
    {drug_data_json}
    
    위 [교과서]에만 100% 근거해서, 이 약의 '핵심 정보 4가지' (1. 약 이름, 2. 효능, 3. 사용법, 4. 핵심 주의 경고)를 
    '음성'으로 듣기 편하게, 매우 '친절한' 대화 말투로 요약해 주세요.
    
    마지막 문장은 반드시 "추가로 궁금한 점이 있으시면 PillBuddy에게 말씀해주세요."라는 문장으로 끝내 주세요.
    [교과서]에 없는 말(환각)은 절대 지어내지 마세요.
    """
    
    try:
        # Gemini API에 '명령서' 전송!
        response = model.generate_content(prompt)
        
        # Gemini가 쓴 '대본'을 '납품'
        print("[부품 2호 / Plan A] '대본' 생성 완료.")
        return response.text
    
    except Exception as e:
        print(f"[부품 2호 / Plan A / 오류!] Gemini API 호출 실패: {e}")
        return "죄송합니다. 약물 정보를 요약하는 데 실패했습니다."


# --- 이게 '메인 공장(app.py)'이 호출할 '부품 2 (Plan B 엔진)' ---
def generate_summary_backup(item_name):
    """
    Plan B: 'e약은요'에 재고가 없을 때 ('itemName'만 받아서),
    Gemini의 '자체 지식'으로 스크립트를 생성합니다.
    """
    
    print(f"[부품 2호 / Plan B] Gemini '자체 지식'으로 '{item_name}' 대본 생성 요청...")
    
    # Gemini한테 보낼 '명령서 (프롬프트)'
    prompt = f"""
    당신은 시각장애인 환자를 돕는 '친절한 약사' AI입니다.
    'e약은요' 공식 DB에는 '{item_name}'의 정보가 없습니다.
    
    대신, 당신이 '일반적으로' 알고 있는 '{item_name}'에 대한 
    '핵심 정보 3가지' (1. 효능, 2. 사용법, 3. 주의 경고)를 
    '음성'으로 듣기 편하게, 매우 '친절한' 대화 말투로 요약해 주세요.
    마지막 문장은 반드시 "추가로 궁금한 점이 있으시면 PillBuddy에게 말씀해주세요."라는 문장으로 끝내 주세요.
    """
    
    try:
        # Gemini API에 '명령서' 전송!
        response = model.generate_content(prompt)
        
        # Gemini가 쓴 '대본'을 '납품'
        print("[부품 2호 / Plan B] '대본' 생성 완료.")
        return response.text
    
    except Exception as e:
        print(f"[부품 2호 / Plan B / 오류!] Gemini API 호출 실패: {e}")
        return "죄송합니다. 약물 정보를 요약하는 데 실패했습니다."


# --- (★ 여기가 '새로 조립'한 기술 3: '추가 질문' (Plan A) ★) ---
def answer_follow_up_with_rag(user_question, rag_data_json):
    """
    [Plan A] '교과서(JSON)'와 '추가 질문'을 받아서 '두 번째' 대답을 생성합니다.
    """
    print(f"[부품 2호 / 기술 3] 'e약은요' 기반으로 '추가 질문'({user_question}) 답변 요청...")
    
    prompt = f"""
    당신은 시각장애인 환자를 돕는 '친절한 약사' AI입니다.
    
    [교과서 (e약은요 API 공식 데이터)]
    {rag_data_json}
    
    [환자의 추가 질문]
    "{user_question}"
    
    위 [교과서]에만 100% 근거해서, 환자의 [추가 질문]에 대해 '친절한' 대화 말투로 답변해 주세요.
    [교과서]에 없는 말(환각)은 절대 지어내지 마세요.
    만약 [교과서]에서 답을 '정말' 찾을 수 없다면, "그 부분은 [교과서]에 기재되어 있지 않아 정확한 답변이 어렵습니다. 의사나 약사와 상담해주세요."라고 솔직하게 말해주세요.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[부품 2호 / 기술 3 / 오류!] Gemini API 호출 실패: {e}")
        return "죄송합니다. 추가 질문에 답변하는 데 실패했습니다."


# --- (★ 여기가 '새로 조립'한 기술 4: '추가 질문' (Plan B) ★) ---
def answer_follow_up_backup(user_question, item_name):
    """
    [Plan B] '약 이름'과 '추가 질문'을 받아서 '두 번째' 대답을 생성합니다.
    """
    print(f"[부품 2호 / 기술 4] '자체 지식'으로 '{item_name}' 추가 질문({user_question}) 답변 요청...")
    
    prompt = f"""
    당신은 시각장애인 환자를 돕는 '친절한 약사' AI입니다.
    'e약은요' 공식 DB에는 '{item_name}'의 정보가 없습니다.
    
    [환자의 추가 질문]
    "{user_question}"
    
    당신이 '일반적으로' 알고 있는 지식을 바탕으로, 환자의 [추가 질문]에 대해 '친절한' 대화 말투로 답변해 주세요.
    답변 마지막에는 "이 답변은 AI의 일반 지식에 기반한 참고용이며, 정확하지 않을 수 있으니 반드시 의사나 약사와 상담하세요."라는 '강력한 경고'를 '꼭' 포함해 주세요.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[부M 2호 / 기술 4 / 오류!] Gemini API 호출 실패: {e}")
        return "죄송합니다. 추가 질문에 답변하는 데 실패했습니다."


# --- (이 파일 자체를 테스트하기 위한 '시동 장치' - '업그레이드') ---
if __name__ == "__main__":
    
    print("--- [부품 2호 공장] 자체 테스트 시작 (v2.0 - 4개 기술 탑재) ---")
    
    # (가짜 '교과서' 미리 준비)
    fake_rag_data = json.dumps([
        {"itemName": "가짜 타이레놀", "useMethodQesitm": "1회 1정", "depositMethodQesitm": "실온 보관"}
    ], indent=2, ensure_ascii=False)
    
    # --- (테스트 1: '첫 요약' - Plan A) ---
    print("\n[테스트 1: '첫 요약' (Plan A)]")
    script1 = generate_summary_with_rag(fake_rag_data)
    print(f" -> {script1[:20]}...") # (결과는 너무 기니까 20자만)
    
    # --- (테스트 2: '첫 요약' - Plan B) ---
    print("\n[테스트 2: '첫 요약' (Plan B)]")
    script2 = generate_summary_backup("아스피린")
    print(f" -> {script2[:20]}...")
    
    # --- (★ '새 기술' 테스트 3: '추가 질문' - Plan A) ---
    print("\n[테스트 3: '추가 질문' (Plan A - RAG)]")
    script3 = answer_follow_up_with_rag("이거 보관 어떻게 해요?", fake_rag_data)
    print("\n--- Plan A 추가 답변 결과 ---")
    print(script3) # (이건 '진짜' 답변이 궁금하니까 '전부' 출력)
    print("----------------------------")
    
    # --- (★ '새 기술' 테스트 4: '추가 질문' - Plan B) ---
    print("\n[테스트 4: '추가 질문' (Plan B - 자체 지식)]")
    script4 = answer_follow_up_backup("이거 술이랑 먹어도 돼요?", "아스피린")
    print("\n--- Plan B 추가 답변 결과 ---")
    print(script4) # (이것도 '전부' 출력)
    print("----------------------------")
    
    print("\n--- [부품 2호 공장] 자체 테스트 종료 ---")