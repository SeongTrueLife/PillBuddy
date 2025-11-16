import streamlit as st
import time
import json 

# --- (부품 공장들 수입) ---
import e_yak_service   # 1호 공장 (팩트 검색기)
import gemini_service  # 2호 공장 (AI 작가)
import speech_service  # 3호 공장 (성우 + 마이크)

# --- (가짜 YOLO 모델) ---
def fake_yolo_model(image_data):
    print("[메인 공장] YOLO 모델이 사진 분석 중... (인 척)")
    time.sleep(2) 
    return "스피드싹연질캡슐" # (Plan A 테스트용)
    # return "아스피린" # (Plan B 테스트용)

# --- (AI 작가 대본 '3단 세척' 함수) ---
def clean_script(script_text):
    cleaned = script_text.replace("**", "") 
    cleaned = cleaned.replace("*", "")  
    cleaned = cleaned.replace("#", "")  
    return cleaned

# --- (메인 공장: Streamlit UI 시작) ---

st.title("👁️ Eye-Pill (v2.2 - '기억' 버그 수정)")

# --- 1. '기억' 초기화 (st.session_state) ---
if 'app_started' not in st.session_state:
    st.session_state['app_started'] = True
    st.session_state['camera_active'] = False # (카메라 '꺼짐' 상태)
    st.session_state['chat_mode'] = False     # (아직 '추가 질문' 모드 아님)
    st.session_state['current_pill_name'] = None 
    st.session_state['current_rag_data'] = None  
    
    speech_service.speak_text("Eye-Pill이 실행되었습니다. 화면 아무 곳이나 터치하여 약 식별을 시작하세요.")

# --- (★ 여기가 '수리'된 '핵심 설계') ---
# --- '상태'에 따라 '단 하나의' 버튼만 보여준다 ---

# (상태 3: '추가 질문' 대기 모드)
if st.session_state['chat_mode']:
    
    st.markdown("---")
    st.subheader(f"'{st.session_state['current_pill_name']}'에 대해 추가 질문하기")
    
    # '추가 질문'용 '화면 전체' 버튼
    if st.button("🎤 추가 질문하기 (화면 아무 곳이나 터치)", use_container_width=True):
        
        speech_service.speak_text("네, 말씀하세요. 마이크가 켜졌습니다.")
        
        user_question = speech_service.listen_from_mic() # (음성 -> 텍스트)
        
        if user_question:
            st.info(f"**[나의 질문]**\n\n{user_question}")
            speech_service.speak_text(f"'{user_question}'에 대해 답변을 준비 중입니다.")

            rag_data = st.session_state['current_rag_data']
            pill_name = st.session_state['current_pill_name']
            
            if rag_data is not None: # (Plan A)
                script = gemini_service.answer_follow_up_with_rag(user_question, rag_data)
            else: # (Plan B)
                script = gemini_service.answer_follow_up_backup(user_question, pill_name)
            
            cleaned = clean_script(script)
            st.markdown(f"**[AI 약사 (추가 답변)]**\n\n{script}") 
            speech_service.speak_text(cleaned)
            # (중요!) 'chat_mode'는 '유지'하고, 'rerun' 없이 '자연스럽게' 대기
            
        else:
            speech_service.speak_text("음성을 인식하지 못했습니다. 다시 시도해주세요.")

# (상태 2: '카메라' 작동 중)
elif st.session_state['camera_active']:
    image_file = st.camera_input("알약을 찍어주세요...", key="camera")
    
    if image_file is not None:
        speech_service.speak_text("사진을 받았습니다. AI가 분석 중입니다.")
        
        pill_name = fake_yolo_model(image_file)
        drug_data_json = e_yak_service.get_drug_info(pill_name)
        
        st.session_state['current_pill_name'] = pill_name
        st.session_state['current_rag_data'] = drug_data_json
        
        if drug_data_json is not None: # (Plan A)
            script = gemini_service.generate_summary_with_rag(drug_data_json)
        else: # (Plan B)
            script = gemini_service.generate_summary_backup(pill_name)
        
        cleaned = clean_script(script)
        st.markdown(f"**[AI 약사 (1차 답변)]**\n\n{script}") 
        speech_service.speak_text(cleaned) 
        
        # '최종' 상태 변경
        st.session_state['camera_active'] = False # 카메라 '끄기'
        st.session_state['chat_mode'] = True      # '추가 질문' 모드 '켜기'!
        # --- (★ 'st.rerun()' 삭제!) ---
        # (Streamlit이 '알아서' 새로고침하게 놔둠)

# (상태 1: '처음' 또는 '새 약 식별' 대기 모드)
else: 
    # (chat_mode도 아니고 camera_active도 아닌 '기본' 상태)
    
    # '약 식별'용 '화면 전체' 버튼
    if st.button("💊 약 식별 시작하기 (화면 아무 곳이나 터치)", use_container_width=True):
        
        st.session_state['chat_mode'] = False
        st.session_state['current_pill_name'] = None
        st.session_state['current_rag_data'] = None
        
        speech_service.speak_text("카메라를 켭니다. 약을 카메라 가까이 보여주세요.")
        st.session_state['camera_active'] = True # "카메라 '켜'!" 라고 '기억'
        # --- (★ 'st.rerun()' 삭제!) ---
        # (버튼 누르면 '알아서' 새로고침됨)