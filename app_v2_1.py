import streamlit as st
import time
import json 

# --- (부품 공장들 수입) ---
import e_yak_service   # 1호 공장 (팩트 검색기)
import gemini_service  # 2호 공장 (AI 작가)
import speech_service  # 3호 공장 (성우 + 마이크) - (수술 완료!)

# --- (★ '웹 전용 스피커' 부품 ★) ---
def play_audio(audio_data):
    """
    서버에서 받은 '음성 데이터(bytes)'를
    Streamlit의 '웹 스피커(st.audio)'로 '즉시' 재생합니다.
    """
    if audio_data:
        print("[메인 공장] 'st.audio'로 음성 데이터 재생 시도...")
        st.audio(audio_data, format="audio/mpeg", start_time=0, autoplay=True)
    else:
        print("[메인 공장 / 오류!] 'play_audio'가 'None' 데이터를 받음.")

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

# (★ 1단계 피드백 적용!) 'layout="wide"' 추가!
st.set_page_config(layout="wide") 

st.title("👁️ PillBuddy (v2.3 - '스피커' 수술)")

# --- 1. '기억' 초기화 (st.session_state) ---
if 'app_started' not in st.session_state:
    st.session_state['app_started'] = True
    st.session_state['camera_active'] = False 
    st.session_state['chat_mode'] = False
    st.session_state['current_pill_name'] = None 
    st.session_state['current_rag_data'] = None 
    
    # (★ '스피커' 수술 적용!)
    audio_data = speech_service.get_speech_data("PillBuddy가 실행되었습니다. 화면 아무 곳이나 터치하여 약 식별을 시작하세요.")
    play_audio(audio_data)

# (상태 3: '추가 질문' 대기 모드)
if st.session_state['chat_mode']:
    
    st.markdown("---")
    st.subheader(f"'{st.session_state['current_pill_name']}'에 대해 추가 질문하기")
    
    # (★ 2단계 피드백 적용!) '고정 안내 멘트' 추가
    # (일단 '음성'은 '봉인'하고 '텍스트'로만 안내)
    st.info("⚠️ '추가 질문(마이크)' 기능은 현재 '수술 중'입니다. (곧 고쳐줄게!)")
    
    # (★ '마이크' 수술 전까지 '임시 봉인'!)
    # if st.button("🎤 추가 질문하기 (화면 아무 곳이나 터치)", use_container_width=True):
        
    #     audio_data = speech_service.get_speech_data("네, 말씀하세요. 마이크가 켜졌습니다.")
    #     play_audio(audio_data)
        
    #     # (★ 여기가 'STT' 수술 부위 -> 일단 '임시 봉인'!)
    #     # user_question = speech_service.listen_from_mic() 
    #     user_question = None # (임시로 'None' 처리)
        
    #     if user_question:
    #         # ... (이하 로직은 일단 봉인) ...
    #         pass
    #     else:
    #         audio_data = speech_service.get_speech_data("음성을 인식하지 못했습니다. 다시 시도해주세요.")
    #         play_audio(audio_data)

# (상태 2: '카메라' 작동 중)
elif st.session_state['camera_active']:
    image_file = st.camera_input("알약을 찍어주세요...", key="camera")
    
    if image_file is not None:
        # (★ '스피커' 수술 적용!)
        audio_data = speech_service.get_speech_data("사진을 받았습니다. AI가 분석 중입니다.")
        play_audio(audio_data)
        
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
        
        # (★ '스피커' 수술 적용!)
        audio_data_main = speech_service.get_speech_data(cleaned) 
        play_audio(audio_data_main)
        
        # (★ 2단계 피드백 적용!) '고정 안내 멘트' 추가
        time.sleep(1) # (메인 음성 끝나고 1초 쉬고)
        audio_data_guide = speech_service.get_speech_data("더 궁금한 점이 있으시면... (현재 '추가 질문' 기능은 수술 중입니다.)")
        play_audio(audio_data_guide)
        
        # '최종' 상태 변경
        st.session_state['camera_active'] = False 
        st.session_state['chat_mode'] = True 
        st.rerun() # (상태 바꿨으니 새로고침!)

# (상태 1: '처음' 또는 '새 약 식별' 대기 모드)
else: 
    if st.button("💊 약 식별 시작하기 (화면 아무 곳이나 터치)", use_container_width=True):
        
        st.session_state['chat_mode'] = False
        st.session_state['current_pill_name'] = None
        st.session_state['current_rag_data'] = None
        
        # (★ 1단계 피드백 적용!) '안내 멘트' 수정
        guide_text = "카메라를 켭니다. 잠시 후, 화면에 나타나는 '알약을 찍어주세요' 영역을 터치하여 촬영해주세요."
        
        # (★ '스피커' 수술 적용!)
        audio_data = speech_service.get_speech_data(guide_text)
        play_audio(audio_data)
        
        st.session_state['camera_active'] = True 
        st.rerun() # (상태 바꿨으니 새로고침!)