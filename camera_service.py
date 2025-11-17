# camera_service.py (공장 4호: '전문 카메라' 엔진룸)

# (★ 수정!) streamlit import 제거 - WebRTC 스레드에서 사용하지 않음
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import av
import threading
from PIL import Image

# 1. '문지기' (Lock)
lock = threading.Lock() 

# 2. '사진 보관함' (Container)
img_container = {"img": None}

# 3. '촬영 신호 깃발' (스레드 안전한 공유 변수)
take_picture_flag = {"value": False}


# --- (★ 여기가 '새 심장'의 '핵심 로직'!) ---
class AutoCameraTransformer(VideoTransformerBase):
    
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        (★ 수정: 스레드 안전한 공유 변수 사용!)
        '매 프레임'마다 '깃발'이 섰는지 '감시'한다.
        WebRTC 스레드에서 안전하게 작동하도록 공유 변수 사용.
        """
        
        # (★ 수정!) 스레드 안전한 공유 변수로 '깃발' 확인
        with lock:
            should_capture = take_picture_flag["value"]
        
        if should_capture:
            print("[공장 4호] '촬영 신호' 감지! 찰칵!")
            
            # 1. "찰칵!" (영상 프레임을 '사진(Image)'으로 변환)
            img = frame.to_image() 
            
            # 2. '안전요원' 부르기 (Lock)
            with lock:
                # 3. '보관함'에 '사진' 넣기
                img_container["img"] = img
                # 4. (★ '초-중요'!) 깃발을 '즉시' 내린다!
                take_picture_flag["value"] = False
                print("[공장 4호] ✅ '사진' 저장 완료! 깃발 내림.")

        # (카메라 '프리뷰'는 '계속' 보여줘야 하니까 'frame'은 '항상' 반환)
        return frame


# --- (★ 이게 '메인 공장'이 '호출'할 '시동 버튼'!) ---
def run_camera_service():
    """
    [공장 4호] '뒷면' 카메라 '엔진'을 '시동' 겁니다.
    카메라 컨텍스트를 반환하여 상태 확인 가능.
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
    
    # (★ 수정!) 카메라 컨텍스트 반환하여 상태 확인 가능하게
    return ctx