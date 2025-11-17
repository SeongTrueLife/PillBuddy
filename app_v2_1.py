import streamlit as st
import time
from PIL import Image

# --- (부품 공장들 수입) ---
import e_yak_service  
import gemini_service  
import speech_service  

# --- ('웹 전용 스피커') ---
def play_audio(audio_data):
    """음성 데이터를 재생합니다."""
    if audio_data:
        print("[메인 공장] 'st.audio'로 음성 데이터 재생 시도...")
        st.audio(audio_data, format="audio/mpeg", start_time=0, autoplay=True)
    else:
        print("[메인 공장 / 오류!] 'play_audio'가 'None' 데이터를 받음.")

# --- (가짜 YOLO 모델) ---
def fake_yolo_model(image_data):
    """약 이미지를 분석하여 약 이름을 반환합니다. (현재는 가짜 모델)"""
    print("[메인 공장] '가짜' YOLO 모델 분석 중... (인 척)")
    time.sleep(2) 
    return "스피드싹연질캡슐" 

# --- (대본 '세척') ---
def clean_script(script_text):
    """마크다운 문법을 제거하여 깔끔한 텍스트로 만듭니다."""
    cleaned = script_text.replace("**", "").replace("*", "").replace("#", "")
    return cleaned

# --- (메인 공장: Streamlit UI 시작) ---
st.set_page_config(
    page_title="PillBuddy",
    page_icon="👁️",
    layout="wide"
) 

# --- 1. '기억' 초기화 ---
if 'app_started' not in st.session_state:
    st.session_state['app_started'] = True
    st.session_state['camera_active'] = False 
    st.session_state['chat_mode'] = False
    st.session_state['current_pill_name'] = None 
    st.session_state['current_rag_data'] = None 
    st.session_state['image_to_process'] = None
    st.session_state['welcome_sound_played'] = False
    st.session_state['camera_guide_played'] = False

# --- (분석 로직: 이미지가 있으면 즉시 처리) ---
if st.session_state['chat_mode'] and st.session_state['image_to_process'] is not None:
    
    captured_image = st.session_state.pop('image_to_process') 
    
    # 음성 안내: 사진 받음
    audio_data_cam = speech_service.get_speech_data("사진을 받았습니다. AI가 분석 중입니다.")
    play_audio(audio_data_cam) 
    
    # 약 분석
    pill_name = fake_yolo_model(captured_image) 
    drug_data_json = e_yak_service.get_drug_info(pill_name)
    
    st.session_state['current_pill_name'] = pill_name
    st.session_state['current_rag_data'] = drug_data_json
    
    # AI 요약 생성
    if drug_data_json is not None: 
        script = gemini_service.generate_summary_with_rag(drug_data_json)
    else: 
        script = gemini_service.generate_summary_backup(pill_name)
    
    cleaned = clean_script(script)
    st.markdown(f"**[AI 약사 (1차 답변)]**\n\n{script}") 
    
    # 음성 재생 준비
    audio_data_main = speech_service.get_speech_data(cleaned) 
    st.session_state['audio_to_play'] = audio_data_main 

# --- (상태 3: 분석 완료 및 추가 질문 대기) ---
if st.session_state['chat_mode']:
    
    st.title("👁️ PillBuddy - 분석 완료") 
    
    # 음성 재생
    if 'audio_to_play' in st.session_state and st.session_state['audio_to_play']:
        main_audio_data = st.session_state.pop('audio_to_play')
        play_audio(main_audio_data)
        
        guide_text = "더 궁금한 점이 있으시면... (현재 '추가 질문' 기능은 수술 중입니다.)"
        guide_audio_data = speech_service.get_speech_data(guide_text)
        play_audio(guide_audio_data)
    
    st.markdown("---")
    st.subheader(f"'{st.session_state['current_pill_name']}'에 대해 추가 질문하기")
    st.info("⚠️ '추가 질문(마이크)' 기능은 현재 '수술 중'입니다.")
    
    # 새 약 식별 버튼
    if st.button("🔄 새 약 식별하기", use_container_width=True, type="primary"):
        st.session_state['chat_mode'] = False
        st.session_state['camera_active'] = False
        st.session_state['welcome_sound_played'] = False
        st.session_state['camera_guide_played'] = False
        st.rerun()

# --- (상태 2: 카메라 촬영 모드) ---
elif st.session_state['camera_active']:
    
    st.title("👁️ PillBuddy - 약 촬영")
    
    # CSS: 시각장애인을 위한 화면 가득 버튼 (프리뷰 숨기기 시도)
    st.markdown("""
        <style>
            /* 카메라 프리뷰 영역 숨기기 */
            div[data-testid="stCameraInput"] > div:first-child {
                display: none !important;
            }
            
            /* 카메라 프리뷰 비디오 숨기기 */
            div[data-testid="stCameraInput"] video {
                display: none !important;
            }
            
            /* 카메라 입력 영역 전체를 버튼 영역으로 */
            div[data-testid="stCameraInput"] {
                width: 100% !important;
                height: 100vh !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* 카메라 촬영 버튼을 화면 가득 크게 */
            div[data-testid="stCameraInput"] button {
                width: 100% !important;
                height: 100vh !important;
                font-size: 3rem !important;
                font-weight: bold !important;
                background-color: #FF4B4B !important;
                color: white !important;
                border: none !important;
                border-radius: 0 !important;
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                z-index: 999 !important;
            }
            
            /* 전체 화면 활용 */
            .main .block-container {
                padding: 0rem !important;
                max-width: 100% !important;
            }
            
            /* 제목 숨기기 (선택적) */
            h1 {
                display: none !important;
            }
            
            /* 취소 버튼 스타일 */
            div.stButton > button {
                width: 100% !important;
                height: 80px !important;
                font-size: 1.5rem !important;
                font-weight: bold !important;
                position: relative !important;
                z-index: 1000 !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 카메라 가이드 음성 (한 번만 재생)
    if not st.session_state['camera_guide_played']:
        guide_text = "약을 카메라 앞에 놓고, 화면 전체를 덮는 큰 빨간 촬영 버튼을 눌러주세요. 버튼은 화면 전체를 차지하고 있습니다."
        audio_data = speech_service.get_speech_data(guide_text)
        play_audio(audio_data)
        st.session_state['camera_guide_played'] = True
        # (★ 수정!) rerun 제거 - 음성이 재생되는 동안 페이지 유지
    
    # st.camera_input 사용 (시각장애인을 위한 화면 가득 버튼)
    # (참고: 프리뷰는 CSS로 숨기고 버튼만 표시)
    captured_image = st.camera_input(
        "약을 카메라 앞에 놓고 화면 전체를 덮는 큰 빨간 촬영 버튼을 눌러주세요",
        key="pill_camera",
        help="약을 카메라 앞에 놓고 화면 전체를 덮는 큰 빨간 촬영 버튼을 눌러주세요."
    )
    
    # 이미지가 촬영되면 즉시 처리
    if captured_image is not None:
        print(f"[메인 공장] ✅ 사진 촬영 완료! 이미지 크기: {captured_image.size}")
        
        # PIL Image로 변환
        img = Image.open(captured_image)
        
        # 상태 변경
        st.session_state['camera_active'] = False
        st.session_state['chat_mode'] = True
        st.session_state['welcome_sound_played'] = False
        st.session_state['camera_guide_played'] = False
        st.session_state['image_to_process'] = img
        
        st.rerun()
    
    # 취소 버튼
    if st.button("❌ 취소", use_container_width=True):
        st.session_state['camera_active'] = False
        st.session_state['welcome_sound_played'] = False
        st.session_state['camera_guide_played'] = False
        st.rerun()

# --- (상태 1: 첫 화면) ---
else: 
    
    # CSS: 전체 화면 버튼
    st.markdown("""
        <style>
            .main .block-container {
                padding: 0rem !important;
            }
            div.stButton {
                height: 100vh !important;
            }
            div.stButton > button {
                height: 100% !important;
                width: 100% !important;
                font-size: 2rem !important;
                font-weight: bold !important;
            }
        </style>
    """, unsafe_allow_html=True) 
    
    button_text = "👁️ PillBuddy\n\n(화면 아무 곳이나 터치하여 시작)"
    
    # 시작 버튼
    if st.button(button_text, use_container_width=True): 
        
        # 첫 번째 클릭: 환영 음성
        if not st.session_state['welcome_sound_played']:
            guide_text = "PillBuddy가 실행되었습니다. 이 음성이 끝나면, 화면 아무 곳이나 다시 한번 터치하여 카메라를 켜주세요."
            audio_data = speech_service.get_speech_data(guide_text)
            play_audio(audio_data)
            st.session_state['welcome_sound_played'] = True
            # (★ 수정!) rerun 제거 - 음성이 재생되는 동안 페이지 유지
        
        # 두 번째 클릭: 카메라 활성화
        else:
            print("[메인 공장] 카메라 활성화...")
            st.session_state['camera_active'] = True
            st.rerun()
