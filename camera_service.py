# camera_service.py (공장 4호: '전문 카메라' 엔진룸)

import streamlit as st
# (🚨 'ClientSettings'는 '삭제'된 상태여야 함!)
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import av
import threading
from PIL import Image

# 1. '문지기' (Lock)
lock = threading.Lock() 

# 2. '사진 보관함' (Container)
img_container = {"img": None}


# --- (★ 여기가 '새 심장'의 '핵심 로직'!) ---
class AutoCameraTransformer(VideoTransformerBase):
    
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        (★ '수술 1' 핵심!)
        '매 프레임'마다 '깃발'이 섰는지 '감시'한다.
        'self.frame_captured' 같은 '자체 기억'을 '삭제'해서,
        '깃발'만 서면 '언제든' 다시 찍을 수 있게 한다!
        """
        
        # '깃발'('take_picture')이 'True'인지 '매 순간' 감시
        if "take_picture" in st.session_state and st.session_state["take_picture"]:
            
            print("[공장 4호] '촬영 신호' 감지! 찰칵!")
            
            # 1. "찰칵!" (영상 프레임을 '사진(Image)'으로 변환)
            img = frame.to_image() 
            
            # 2. '안전요원' 부르기 (Lock)
            with lock:
                # 3. '보관함'에 '사진' 넣기
                img_container["img"] = img
            
            # 4. (★ '초-중요'!) 깃발을 '즉시' 내린다! (이게 '일꾼'의 '새 임무'!)
            st.session_state["take_picture"] = False

        # (카메라 '프리뷰'는 '계속' 보여줘야 하니까 'frame'은 '항상' 반환)
        return frame


# --- (★ 이게 '메인 공장'이 '호출'할 '시동 버튼'!) ---
def run_camera_service():
    """
    [공장 4호] '뒷면' 카메라 '엔진'을 '시동' 겁니다.
    """
    
    video_constraints = {"facingMode": "environment"} 

    ctx = webrtc_streamer(
        key="webrtc-camera", 
        
        # (★ '수술 1' 핵심! '자동 시동'!)
        desired_playing_state=True, 
        
        mode=WebRtcMode.RECVONLY, 
        video_transformer_factory=AutoCameraTransformer, 
        media_stream_constraints={"video": video_constraints, "audio": False},
        async_processing=True, 
        
        # (★ 'ClientSettings' 삭제' -> 'rtc_configuration'만 남김!)
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        
        video_html_attrs={
            "style": "display: none;", # (★ '프리뷰'는 '숨기기'!)
            "autoPlay": True, 
            "controls": False, 
            "muted": True,
        }
    )
    
    # (★ '성격 급한' '메인 공장'을 위해 '아무것도' 반환하지 않음!)
    # (★ '보관함' 확인은 '메인 공장'이 '직접' 하도록 '변경'!)