import streamlit as st
import time
import json 

# --- (부품 공장들 수입) ---
import e_yak_service 
import gemini_service 
import speech_service 
import camera_service 

# --- ('웹 전용 스피커') ---
def play_audio(audio_data):
    if audio_data:
        print("[메인 공장] 'st.audio'로 음성 데이터 재생 시도...")
        st.audio(audio_data, format="audio/mpeg", start_time=0, autoplay=True)
    else:
        print("[메인 공장 / 오류!] 'play_audio'가 'None' 데이터를 받음.")

# --- (가짜 YOLO 모델) ---
def fake_yolo_model(image_data):
    print("[메인 공장] '가짜' YOLO 모델 분석 중... (인 척)")
    time.sleep(2) 
    return "스피드싹연질캡슐" 

# --- (대본 '세척') ---
def clean_script(script_text):
    cleaned = script_text.replace("**", "").replace("*", "").replace("#", "")
    return cleaned

# --- (메인 공장: Streamlit UI 시작) ---
st.set_page_config(layout="wide") 

# --- 1. '기억' 초기화 ---
if 'app_started' not in st.session_state:
    st.session_state['app_started'] = True
    st.session_state['camera_active'] = False 
    st.session_state['chat_mode'] = False
    st.session_state['current_pill_name'] = None 
    st.session_state['current_rag_data'] = None 
    st.session_state['take_picture'] = False 
    st.session_state['state2_first_run'] = True # '상태 2' 첫 진입 '깃발'
    st.session_state['analysis_pending'] = False # (★ '분석' 대기 '깃발'!)

# --- (★ '성격 급한 놈' 고치기 - '수술 2' 핵심!) ---
# (★ '사진 보관함'을 '먼저' 확인하는 '새 로직'!)

# '보관함'('img_container')이 '찼는지' '먼저' 확인!
with camera_service.lock:
    captured_image = camera_service.img_container["img"]

# (★ '분석' 대기 깃발이 '서 있고' + '보관함'이 '찼다'면!)
if st.session_state['analysis_pending'] and captured_image is not None:
    
    # '보관함' '즉시' 비우기!
    with camera_service.lock:
        camera_service.img_container["img"] = None
    
    # '깃발' 내리기!
    st.session_state['analysis_pending'] = False
    
    # --- (★ '분석' & '상태 3' 로직 '시작'!) ---
    audio_data_cam = speech_service.get_speech_data("사진을 받았습니다. AI가 분석 중입니다.")
    play_audio(audio_data_cam) # (★ '여기서' 트는 건 '안전'함!)
    
    pill_name = fake_yolo_model(captured_image) 
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
    st.session_state['audio_to_play'] = audio_data_main # '상태 3'에서 쓸 '음성'
    
    # '상태' 변경!
    st.session_state['camera_active'] = False 
    st.session_state['chat_mode'] = True 
    st.session_state['state2_first_run'] = True # (다음을 위해 '깃발' 리셋)
    
    st.rerun() # ('상태 3'으로 '이동'!)

# (상태 3: '추가 질문' 대기 모드)
elif st.session_state['chat_mode']:
    
    st.title("👁️ PillBuddy (v2.7 - 분석 완료)") 
    
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
    
    st.title("👁️ PillBuddy (v2.7 - 촬영 대기)")
    
    # (CSS 마법)
    st.markdown("""
        <style>
            .main .block-container { padding: 0rem; }
            div.stButton { height: 100vh; }
            div.stButton > button { height: 100%; width: 100%; font-size: 1.5rem; }
        </style>
    """, unsafe_allow_html=True)
    
    # ('촬영' 버튼!)
    if st.button("📸 촬영하기 (화면 아무 곳이나 터치)", use_container_width=True):
        st.session_state["take_picture"] = True # (★ '일꾼'에게 '깃발'만 세움!)
        st.session_state['analysis_pending'] = True # (★ '방송국'에 '대기' 깃발 세움!)
        
        # (★ '성격 급한 놈'을 위해 '일부러' 0.5초 '기다려줌'!)
        # (★ '일꾼'이 '사진' 찍을 '시간'을 벌어주는 '마법'!)
        time.sleep(0.5) 
        st.rerun() # (★ '스스로' '새로고침'해서 '보관함' 확인하러 감!)

    # (★ 'CCTV'는 '조용히' '항상' 켜 둠)
    camera_service.run_camera_service()

    # (★ '방송국' 충돌 해결!)
    # (★ 'CCTV'가 '켜진 후'에 '스피커'를 켜야 '안전'함!)
    if st.session_state['state2_first_run']:
        guide_text = "PillBuddy가 실행되었습니다. 카메라가 켜집니다. 약을 준비하고, 화면 아무 곳이나 터치해 촬영해주세요."
        audio_data = speech_service.get_speech_data(guide_text)
        play_audio(audio_data) 
        st.session_state['state2_first_run'] = False # ('깃발' 내려서 '반복 재생' 방지!)

# (상태 1: '처음' 또는 '새 약 식별' 대기 모드)
else: 
    # (CSS 마법)
    st.markdown("""
        <style>
            .main .block-container { padding: 0rem; }
            div.stButton { height: 100vh; }
            div.stButton > button { height: 100%; width: 100%; font-size: 1.5rem; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True) 
    
    button_text = "👁️ PillBuddy\n\n(화면 아무 곳이나 터치하여 시작)"
    
    # (★ '방송국' 충돌 해결!) '소리' 빼고 '즉시' 이동!
    if st.button(button_text, use_container_width=True): 
        st.session_state['camera_active'] = True # ('상태 2'로 '이동'!)
        st.rerun() # ('강제' 이동!)