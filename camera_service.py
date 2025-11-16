# camera_service.py (공장 4호: '전문 카메라' 엔진룸)

import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import av  # (이건 '비디오 프레임'을 다루는 '특수 부품')
import threading # (이건 '동시 작업'을 위한 '안전장치')
from PIL import Image # (이건 '이미지'를 다루는 '표준 부품')

# --- (★ 여기가 'v2.7' 수술의 '핵심'!) ---
# 'streamlit-webrtc'는 '백그라운드'에서 '동시에' 돌아가기 때문에,
# '메인 공장'과 '안전하게' 사진을 주고받을 '장치'가 필요해.

# 1. '문지기' (Lock)
# (메인 공장과 카메라 공장이 '동시에' '보관함'을 건드리지 못하게 막는 '안전요원')
lock = threading.Lock() 

# 2. '사진 보관함' (Container)
# (카메라가 '찍은' 사진을 '임시'로 보관할 '상자')
img_container = {"img": None}


# --- (★ 여기가 '새 심장'의 '핵심 로직'!) ---
class AutoCameraTransformer(VideoTransformerBase):
    """
    이 '엔진'은 'webrtc_streamer'에 '장착'되어서,
    '매 순간(frame)'마다 '비밀 신호'가 왔는지 '감시'하는 역할을 해.
    """
    
    def __init__(self):
        self.frame_captured = False # (★ '자동 촬영'은 '단 한 번'만!)
    
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        이 'recv' 함수는 카메라 영상의 '매 순간(frame)'마다 '자동'으로 '실행'돼.
        (1초에 30번~60번!)
        """
        
        # '자동 촬영'을 '아직' 안 했는지 '확인'
        if not self.frame_captured:
            
            # (★ 여기가 '자동 촬영'의 '핵심'!)
            # "혹시 '메인 공장'에서 '비밀 신호(take_picture)'를 보냈나?"
            if "take_picture" in st.session_state and st.session_state["take_picture"]:
                
                print("[공장 4호] '촬영 신호' 감지! 찰칵!")
                
                # 1. "찰칵!" (영상 프레임을 '사진(Image)'으로 변환)
                img = frame.to_image() 
                
                # 2. '안전요원' 부르기 (Lock)
                with lock:
                    # 3. '보관함'에 '사진' 넣기
                    img_container["img"] = img
                
                # 4. "촬영 끝났음!" ('깃발' 올리기)
                self.frame_captured = True
                
                # 5. '메인 공장'에 보낸 '비밀 신호'를 '리셋' (중요!)
                st.session_state["take_picture"] = False

        # (카메라 '프리뷰'는 '계속' 보여줘야 하니까 'frame'은 '항상' 반환)
        return frame


# --- (★ 이게 '메인 공장'이 '호출'할 '시동 버튼'!) ---
def run_camera_service():
    """
    [공장 4호] '뒷면' 카메라 '엔진'을 '시동' 겁니다.
    'AutoCameraTransformer' 엔진을 장착하여 '자동 촬영' 신호를 '대기'합니다.
    """
    
    # (★ 여기가 '뒷면 카메라'를 켜는 '마법의 코드'!)
    video_constraints = {"facingMode": "environment"} # "environment" = 뒷면!

    # (★ 'WebRTC' 엔진 '본체'!)
    ctx = webrtc_streamer(
        key="webrtc-camera", # (이 '엔진'의 '이름표')
        
        mode=WebRtcMode.RECVONLY, # (우리는 '받기(RECV)'만 할 거니까)
        
        # (★ '방금 만든' '자동 촬영' 엔진 '장착'!)
        video_transformer_factory=AutoCameraTransformer, 
        
        # (★ '뒷면 카메라'로 켜!)
        media_stream_constraints={"video": video_constraints, "audio": False},
        
        async_processing=True, # (백그라운드에서 '부드럽게' 돌리기)
        
        # (★ '시각장애인'을 위해 '쓸데없는' '컨트롤 바'는 '숨기기'!)
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        video_html_attrs={
            "style": "width: 100%; height: auto; border: 1px solid #ccc; transform: scaleX(-1);", 
            "autoPlay": True, 
            "controls": False, 
            "muted": True,
        }
    )
    
    # (★ '엔진'이 '가동'되는 '동안'...)
    if ctx.state.playing:
        # '안전요원'의 '감시' 하에 '보관함'을 '확인'
        with lock:
            captured_image = img_container["img"]
        
        # "어! '보관함'에 '사진'이 들어왔네?"
        if captured_image is not None:
            print("[공장 4호] '보관함'에서 '캡처된 사진' 발견! '메인 공장'으로 '반환'!")
            
            # '보관함' 비우기 (다음 촬영을 위해)
            with lock:
                img_container["img"] = None
            
            # (★ 여기가 '최종 결과물'!)
            # '메인 공장'에 '사진'을 '납품'!
            return captured_image 
            
    # (아직 '촬영 신호'가 안 왔거나, '엔진'이 '꺼져' 있으면 'None' 납품)
    return None