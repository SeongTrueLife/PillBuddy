# camera_service.py (공장 4호: v2.7.3 - '최신 심장' 버전)

import streamlit as st
# (★ v2.7.3 수술 1!) '단종된' 'ClientSettings'를 '삭제'함!
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode 
import av  
import threading 
from PIL import Image 

# --- ('문지기'와 '보관함'은 '그대로' 유지!) ---
lock = threading.Lock() 
img_container = {"img": None}

# --- ('핵심 로직'도 '그대로' 유지!) ---
class AutoCameraTransformer(VideoTransformerBase):
    
    def __init__(self):
        self.frame_captured = False 
    
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        
        if not self.frame_captured:
            if "take_picture" in st.session_state and st.session_state["take_picture"]:
                
                print("[공장 4호] '촬영 신호' 감지! 찰칵!")
                img = frame.to_image() 
                
                with lock:
                    img_container["img"] = img
                
                self.frame_captured = True
                st.session_state["take_picture"] = False

        return frame

# --- (★ 이게 '메인 공장'이 '호출'할 '시동 버튼'!) ---
def run_camera_service():
    
    video_constraints = {"facingMode": "environment"} 

    # (★ v2.7.3 수술 2!) 'ClientSettings' '덩어리'를 '제거'하고,
    # '알맹이'인 'rtc_configuration'만 '밖으로' '꺼냄'!
    ctx = webrtc_streamer(
        key="webrtc-camera", 
        mode=WebRtcMode.RECVONLY, 
        video_transformer_factory=AutoCameraTransformer, 
        media_stream_constraints={"video": video_constraints, "audio": False},
        async_processing=True, 
        
        # (★ 여기가 '수술' 부위!)
        # 'client_settings=ClientSettings(...)' '삭제' -> 'rtc_configuration'만 '남김'!
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        
        video_html_attrs={
            "style": "width: 100%; height: auto; border: 1px solid #ccc; transform: scaleX(-1);", 
            "autoPlay": True, 
            "controls": False, 
            "muted": True,
        }
    )
    
    if ctx.state.playing:
        with lock:
            captured_image = img_container["img"]
        
        if captured_image is not None:
            print("[공장 4호] '보관함'에서 '캡처된 사진' 발견! '메인 공장'으로 '반환'!")
            with lock:
                img_container["img"] = None
            return captured_image 
            
    return None