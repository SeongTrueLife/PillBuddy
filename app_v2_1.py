import streamlit as st
import time
import json 

# --- (부품 공장들 수입) ---
import e_yak_service   
import gemini_service  
import speech_service  

# --- ('웹 전용 스피커' - (수정 없음)) ---
def play_audio(audio_data):
    if audio_data:
        print("[메인 공장] 'st.audio'로 음성 데이터 재생 시도...")
        st.audio(audio_data, format="audio/mpeg", start_time=0, autoplay=True)
    else:
        print("[메인 공장 / 오류!] 'play_audio'가 'None' 데이터를 받음.")

# --- (가짜 YOLO 모델 - (수정 없음)) ---
def fake_yolo_model(image_data):
    print("[메인 공장] YOLO 모델이 사진 분석 중... (인 척)")
    time.sleep(2) 
    return "스피드싹연질캡슐" 
    # return "아스피린" 

# --- (AI 작가 대본 '세척' 함수 - (수정 없음)) ---
def clean_script(script_text):
    cleaned = script_text.replace("**", "").replace("*", "").replace("#", "")
    return cleaned

# --- (메인 공장: Streamlit UI 시작) ---
st.set_page_config(layout="wide") # (이건 '계속' 가져감!)
# (★ v2.6!) '제목'은 '상태 1'에서는 '숨김'

# --- 1. '기억' 초기화 ---
if 'app_started' not in st.session_state:
    st.session_state['app_started'] = True
    st.session_state['camera_active'] = False 
    st.session_state['chat_mode'] = False
    st.session_state['current_pill_name'] = None 
    st.session_state['current_rag_data'] = None 
    
# (상태 3: '추가 질문' 대기 모드)
if st.session_state['chat_mode']:
    
    st.title("👁️ PillBuddy (v2.6)") # (★ v2.6!) '상태 3'에서 '제목' 표시!
    
    # (v2.4에서 수술한 '재생' 로직 - (그대로 유지!))
    if 'audio_to_play' in st.session_state and st.session_state['audio_to_play']:
        main_audio_data = st.session_state.pop('audio_to_play')
        play_audio(main_audio_data)
        
        guide_text = "더 궁금한 점이 있으시면... (현재 '추가 질문' 기능은 수술 중입니다.)"
        guide_audio_data = speech_service.get_speech_data(guide_text)
        play_audio(guide_audio_data)
    
    st.markdown("---")
    st.subheader(f"'{st.session_state['current_pill_name']}'에 대해 추가 질문하기")
    st.info("⚠️ '추가 질문(마이크)' 기능은 현재 '수술 중'입니다.")
    
# (상태 2: '카메라' 작동 중)
elif st.session_state['camera_active']:
    
    st.title("👁️ PillBuddy (v2.6)") # (★ v2.6!) '상태 2'에서 '제목' 표시!
    
    # (v2.4에서 수술한 '처리' 로직 - (그대로 유지!))
    image_file = st.camera_input("알약을 찍어주세요...", key="camera")
    
    if image_file is not None:
        audio_data_cam = speech_service.get_speech_data("사진을 받았습니다. AI가 분석 중입니다.")
        play_audio(audio_data_cam)
        
        pill_name = fake_yolo_model(image_file)
        drug_data_json = e_yak_service.get_drug_info(pill_name)
        
        st.session_state['current_pill_name'] = pill_name
        st.session_state['current_rag_data'] = drug_data_json
        
        if drug_data_json is not None: 
            script = gemini_service.generate_summary_with_rag(drug_data_json)
        else: 
            script = gemini_service.generate_summary_backup(pill_name)
        
        cleaned = clean_script(script)
        st.markdown(f"**[AI 약사 (1차 답변)]**\n\n{script}") 
        
        audio_data_main = speech_service.get_speech_data(cleaned) 
        st.session_state['audio_to_play'] = audio_data_main
        
        st.session_state['camera_active'] = False 
        st.session_state['chat_mode'] = True 
        st.rerun() 

# (상태 1: '처음' 또는 '새 약 식별' 대기 모드)
else: 
    # (★ 여기가 'v2.6' 'CSS 마법'이 '주입'되는 곳!)
    st.markdown("""
        <style>
            /* Streamlit의 '메인 영역'의 '안쪽 여백'을 싹 다 없애버려! */
            .main .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
                padding-left: 0rem;
                padding-right: 0rem;
            }
            
            /* '버튼'이 들어있는 'div'를 화면 100% 높이로! */
            div.stButton {
                height: 100vh; /* (vh = Viewport Height = 화면 높이) */
            }
            
            /* '버튼' 자체를 그 'div'에 꽉 채워! (높이 100%) */
            div.stButton > button {
                height: 100%; 
                width: 100%;
                font-size: 1.5rem; /* (글자 크기도 좀 키우자!) */
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True) 
    
    # (★ 'v2.6' - 네 '아이디어'가 '적용'된 '거대한' 버튼!)
    button_text = "👁️ PillBuddy\n\n(화면 아무 곳이나 터치하여 시작)"
    if st.button(button_text, use_container_width=True): 
        
        # (v2.4 로직: '터치 직후'에 '첫 음성' 재생!)
        guide_text = "PillBuddy가 실행되었습니다. 카메라를 켭니다. 잠시 후, '알약을 찍어주세요' 영역을 터치하여 촬영해주세요."
        audio_data = speech_service.get_speech_data(guide_text)
        play_audio(audio_data) 
        
        st.session_state['chat_mode'] = False
        st.session_state['current_pill_name'] = None
        st.session_state['current_rag_data'] = None
        st.session_state['camera_active'] = True