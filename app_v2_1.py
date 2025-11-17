import streamlit as st
import time
from PIL import Image
from io import BytesIO

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
    
    # 제목을 작게 표시 (또는 숨기기)
    st.markdown("### 👁️ PillBuddy - 약 촬영")
    
    # CSS: 시각장애인을 위한 큰 버튼
    st.markdown("""
        <style>
            /* 제목을 작게 (또는 완전히 숨기려면 display: none 사용) */
            h3 {
                font-size: 1rem !important;
                margin-bottom: 0.5rem !important;
                padding: 0.25rem 0 !important;
            }
            
            /* 카메라 프리뷰를 작게 (상단에 작게 표시) */
            div[data-testid="stCameraInput"] video {
                width: 100% !important;
                max-height: 200px !important;
                object-fit: cover !important;
            }
            
            /* 카메라 입력 영역 */
            div[data-testid="stCameraInput"] {
                width: 100% !important;
                margin-bottom: 1rem !important;
            }
            
            /* 카메라 촬영 버튼을 화면 가득 크게 */
            div[data-testid="stCameraInput"] button {
                width: 100% !important;
                height: 120px !important;
                min-height: 120px !important;
                font-size: 3rem !important;
                font-weight: bold !important;
                background-color: #FF4B4B !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                margin-top: 1rem !important;
            }
            
            /* 전체 화면 활용 */
            .main .block-container {
                padding: 0.5rem !important;
                max-width: 100% !important;
            }
            
            /* 취소 버튼 스타일 */
            div.stButton > button {
                width: 100% !important;
                height: 70px !important;
                font-size: 1.8rem !important;
                font-weight: bold !important;
            }
        </style>
        
    """, unsafe_allow_html=True)
    
    # 카메라 가이드 음성 (한 번만 재생)
    if not st.session_state['camera_guide_played']:
        guide_text = (
            "지금은 전면 카메라가 켜졌습니다. 약을 얼굴 쪽으로 들어 올려 전면 카메라에 잘 보이도록 한 뒤, "
            "화면 맨 아래 가운데에 있는 큰 빨간 'Take Photo' 버튼을 눌러주세요. "
            "만약 후면 카메라로 찍고 싶으시다면, 카메라 프리뷰 오른쪽 가장자리 중간에 있는 작은 '카메라 전환' 버튼을 눌러 후면 카메라로 전환하신 뒤 촬영해주세요."
        )
        audio_data = speech_service.get_speech_data(guide_text)
        play_audio(audio_data)
        st.session_state['camera_guide_played'] = True
        # (★ 수정!) rerun 제거 - 음성이 재생되는 동안 페이지 유지
    
    # st.camera_input 사용 (프리뷰는 작게, 버튼은 크게)
    captured_image = st.camera_input(
        "약을 전면 카메라에 보이도록 들어 올린 뒤, 아래의 큰 빨간 촬영 버튼을 눌러주세요",
        key="pill_camera",
        help="약을 카메라 앞에 들어 올린 뒤, 필요하면 오른쪽의 작은 버튼으로 후면 카메라로 전환한 후 아래의 큰 빨간 버튼을 눌러 촬영하세요."
    )
    
    # 이미지가 촬영되면 즉시 처리
    if captured_image is not None:
        try:
            # UploadedFile을 PIL Image로 변환
            # 방법 1: getvalue()로 바이트 데이터 읽기
            image_bytes = captured_image.getvalue()
            print(f"[메인 공장] ✅ 사진 촬영 완료! 이미지 바이트 크기: {len(image_bytes)}")
            
            # BytesIO로 변환 후 PIL Image로 열기
            img = Image.open(BytesIO(image_bytes))
            print(f"[메인 공장] ✅ PIL Image 변환 성공! 이미지 크기: {img.size}")
            
            # 상태 변경
            st.session_state['camera_active'] = False
            st.session_state['chat_mode'] = True
            st.session_state['welcome_sound_played'] = False
            st.session_state['camera_guide_played'] = False
            st.session_state['image_to_process'] = img
            
            st.rerun()
            
        except Exception as e:
            print(f"[메인 공장 / 오류!] 이미지 처리 실패: {e}")
            st.error(f"이미지 처리 중 오류가 발생했습니다: {e}")
            st.info("다시 촬영해주세요.")
    
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
