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

# --- 1. '기억' 초기화 (★ '수술' 핵심!) ---
if 'app_started' not in st.session_state:
    st.session_state['app_started'] = True
    st.session_state['camera_active'] = False 
    st.session_state['chat_mode'] = False
    st.session_state['current_pill_name'] = None 
    st.session_state['current_rag_data'] = None 
    st.session_state['image_to_process'] = None
    st.session_state['welcome_sound_played'] = False # (★ '환영 음성' '깃발'!)
    st.session_state['checking_for_image'] = False # (★ '사장님' '대기' '깃발'!)

# --- (★ '수술' 핵심!) '분석' 로직을 '맨 위'로 뺌! ---
if st.session_state['chat_mode'] and st.session_state['image_to_process'] is not None:
    
    captured_image = st.session_state.pop('image_to_process') 
    
    # --- (★ '분석' & '상태 3' '음성' 로직 '시작'!) ---
    # (★ 'CCTV'가 '꺼진' '안전한' 상태라 '무조건' '성공'!)
    audio_data_cam = speech_service.get_speech_data("사진을 받았습니다. AI가 분석 중입니다.")
    play_audio(audio_data_cam) 
    
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

# (상태 3: '추가 질문' 대기 모드)
if st.session_state['chat_mode']:
    
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

# (상태 2: '카메라' 작동 중 - (★ 'CCTV' '전용' 방!))
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
    
    # (★ 수정!) 카메라 서비스 실행 및 상태 확인
    ctx = camera_service.run_camera_service()
    
    # (★ 수정!) 카메라가 실제로 작동 중인지 확인
    camera_ready = ctx.state.playing if ctx else False
    
    if not camera_ready:
        st.info("📷 카메라를 초기화하는 중입니다... 잠시만 기다려주세요.")
        st.rerun()
    
    # ('촬영' 버튼!)
    if st.button("📸 촬영하기 (화면 아무 곳이나 터치)", use_container_width=True):
        # (★ 수정!) 공유 변수로 '깃발' 세움
        with camera_service.lock:
            camera_service.take_picture_flag["value"] = True
        st.session_state["checking_for_image"] = True
        print("[메인 공장] '촬영 신호' 전송! (공유 변수에 깃발 세움)")
        st.rerun()

    # (★ 수정!) '사진' 확인 로직 (폴링 방식 개선)
    if st.session_state["checking_for_image"]:
        
        # (★ '보관함' '확인'!)
        captured_image = None
        with camera_service.lock:
            if camera_service.img_container["img"] is not None:
                captured_image = camera_service.img_container["img"]
                camera_service.img_container["img"] = None
                print("[메인 공장] ✅ '사진' 발견! '상태 3'로 이동 준비...")

        # (★ "어! '보관함'에 '사진'이 들어왔다!")
        if captured_image is not None:
            # (★ '이사' 준비!)
            st.session_state['checking_for_image'] = False
            st.session_state['camera_active'] = False
            st.session_state['chat_mode'] = True
            st.session_state['welcome_sound_played'] = False
            st.session_state['image_to_process'] = captured_image 
            st.rerun() # (★ '상태 3' ('맨 위' 분석)로 '이동'!)
        
        # (★ 수정!) "아직... '사진'이 '안' 왔다..." - 자동 재확인
        else:
            print("[메인 공장] ⏳ '사진' 아직 없음... 잠시 후 다시 확인...")
            st.info("📸 촬영 중... 잠시만 기다려주세요.")
            # (★ 수정!) time.sleep 대신 Streamlit의 자동 rerun 활용
            # 짧은 딜레이 후 자동으로 재확인 (무한 루프 방지를 위해 최대 재시도는 Streamlit이 관리)
            time.sleep(0.3)  # (★ 최소한의 딜레이만 사용 - 너무 짧으면 서버 부하)
            st.rerun()

# (상태 1: '처음' 또는 '새 약 식별' 대기 모드 - (★ '스피커' '전용' 방!))
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
    
    # (★ '수술' 핵심! '두 번'의 '탭'을 '설계'한다!)
    if st.button(button_text, use_container_width=True): 
        
        # (★ '첫 번째' 탭인가?)
        if not st.session_state['welcome_sound_played']:
            
            # (★ '안내 멘트' 수정!)
            guide_text = "PillBuddy가 실행되었습니다. 이 음성이 끝나면, 화면 아무 곳이나 '다시 한번' 터치하여 카메라를 켜주세요."
            audio_data = speech_service.get_speech_data(guide_text)
            play_audio(audio_data) # (★ 'CCTV' 없으니 '안전'!)
            
            st.session_state['welcome_sound_played'] = True # ('깃발' 세움!)
            # (★ 'rerun'이 '없어서' '소리'가 '끝까지' 나옴!)
        
        # (★ '두 번째' 탭인가?)
        else:
            st.session_state['camera_active'] = True # ('상태 2'로 '이동'!)
            st.rerun() # ('강제' 이동!)