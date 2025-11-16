import streamlit as st
import time
import json 

# --- (부품 공장들 수입) ---
import e_yak_service   
import gemini_service  
import speech_service  
import camera_service # (★ v2.7!) '공장 4호' ('새 심장') 수입!

# --- ('웹 전용 스피커' - (수정 없음)) ---
def play_audio(audio_data):
    if audio_data:
        print("[메인 공장] 'st.audio'로 음성 데이터 재생 시도...")
        st.audio(audio_data, format="audio/mpeg", start_time=0, autoplay=True)
    else:
        print("[메인 공장 / 오류!] 'play_audio'가 'None' 데이터를 받음.")

# --- (가짜 YOLO 모델 - (수정 없음)) ---
def fake_yolo_model(image_data):
    # (★ v2.7!) 이 'image_data'는 이제 '진짜' PIL Image 객체임!
    print("[메인 공장] '진짜' 이미지 데이터로 YOLO 모델 분석 중... (인 척)")
    time.sleep(2) 
    return "스피드싹연질캡슐" 
    # return "아스피린" 

# --- (AI 작가 대본 '세척' 함수 - (수정 없음)) ---
def clean_script(script_text):
    cleaned = script_text.replace("**", "").replace("*", "").replace("#", "")
    return cleaned

# --- (메인 공장: Streamlit UI 시작) ---
st.set_page_config(layout="wide") 
# (★ v2.7!) '제목'은 '상태'에 따라 '선별적'으로 표시

# --- 1. '기억' 초기화 ---
if 'app_started' not in st.session_state:
    st.session_state['app_started'] = True
    st.session_state['camera_active'] = False 
    st.session_state['chat_mode'] = False
    st.session_state['current_pill_name'] = None 
    st.session_state['current_rag_data'] = None 
    st.session_state['take_picture'] = False # (★ v2.7!) '촬영 신호' 초기화

# --- (★ 여기가 'v2.7' '심장 이식'의 '핵심'!) ---

# (상태 3: '추가 질문' 대기 모드)
if st.session_state['chat_mode']:
    
    st.title("👁️ PillBuddy (v2.7)") # ('제목' 표시 O)
    
    # (v2.4 '재생' 로직 - (그대로 유지!))
    if 'audio_to_play' in st.session_state and st.session_state['audio_to_play']:
        main_audio_data = st.session_state.pop('audio_to_play')
        play_audio(main_audio_data)
        
        guide_text = "더 궁금한 점이 있으시면... (현재 '추가 질문' 기능은 수술 중입니다.)"
        guide_audio_data = speech_service.get_speech_data(guide_text)
        play_audio(guide_audio_data)
    
    st.markdown("---")
    st.subheader(f"'{st.session_state['current_pill_name']}'에 대해 추가 질문하기")
    st.info("⚠️ '추가 질문(마이크)' 기능은 현재 '수술 중'입니다.")
    
# (상태 2: '카메라' 작동 중 - (★ '심장 이식' 수술 '본체'!) ★)
elif st.session_state['camera_active']:
    
    st.title("👁️ PillBuddy (v2.7)") # ('제목' 표시 O)
    
    # (★ v2.7!) '공장 4호'의 'CSS 마법'을 '여기서도' 쓴다!
    # ('촬영' 버튼도 '전체 화면'으로 만들기 위해!)
    st.markdown("""
        <style>
            .main .block-container { padding: 0rem; }
            div.stButton { height: 100vh; }
            div.stButton > button { height: 100%; width: 100%; font-size: 1.5rem; }
        </style>
    """, unsafe_allow_html=True)
    
    # (★ v2.7!) '촬영' 버튼! (이것도 '전체 화면'임!)
    if st.button("📸 촬영하기 (화면 아무 곳이나 터치)", use_container_width=True):
        # (★ v2.7!) '공장 4호'에 "찍어!"라는 '비밀 신호' 전송!
        st.session_state["take_picture"] = True
        # st.rerun() # ('신호' 보냈으니 '새로고침'해서 '공장 4호'가 '알아채게' 함! -> 버그로 삭제)

    # (★ v2.7!) '공장 4호'('새 심장') '가동'!!!
    # 이 'run_camera_service'가 '뒷면 카메라'를 '보여주고',
    # '비밀 신호'가 오면 '사진'을 '반환'한다!
    captured_image = camera_service.run_camera_service()
    
    # (★ vK.7!) "어! '공장 4호'가 '사진'을 '납품'했다!"
    if captured_image is not None:
        
        # (v2.4 '처리' 로직 - (그대로 유지!))
        audio_data_cam = speech_service.get_speech_data("사진을 받았습니다. AI가 분석 중입니다.")
        play_audio(audio_data_cam)
        
        # (★ v2.7!) '가짜 YOLO'에 '진짜' 이미지를 넣는다!
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
        st.session_state['audio_to_play'] = audio_data_main
        
        # '상태' 변경! (카메라 끄고 -> 채팅 모드로!)
        st.session_state['camera_active'] = False 
        st.session_state['chat_mode'] = True 
        st.rerun() # ('상태 3'으로 '이동'!)

# (상태 1: '처음' 또는 '새 약 식별' 대기 모드)
else: 
    # (★ v2.6 'CSS 마법' - (그대로 유지!))
    st.markdown("""
        <style>
            .main .block-container { padding: 0rem; }
            div.stButton { height: 100vh; }
            div.stButton > button { height: 100%; width: 100%; font-size: 1.5rem; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True) 
    
    # (★ v2.6 '전체 화면' 버튼 - (그대로 유지!))
    button_text = "👁️ PillBuddy\n\n(화면 아무 곳이나 터치하여 시작)"
    if st.button(button_text, use_container_width=True): 
        
        # ('터치 직후' '첫 음성' 재생!)
        guide_text = "PillBuddy가 실행되었습니다. 카메라가 켜집니다. 약을 준비하고, 잠시 후 '촬영' 버튼이 나타나면 화면을 다시 터치해 촬영해주세요."
        audio_data = speech_service.get_speech_data(guide_text)
        play_audio(audio_data) 
        
        st.session_state['camera_active'] = True # ('상태 2'로 '이동'!)
        st.rerun()