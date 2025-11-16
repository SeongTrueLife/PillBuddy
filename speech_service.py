# speech_service.py

import azure.cognitiveservices.speech as speechsdk
import config # 1. '금고'를 수입(import)한다!

# --- (열쇠를 '금고'에서 꺼내 쓰도록 수정!) ---
SPEECH_KEY = config.AZURE_SPEECH_KEY         # 2. '금고'에서 꺼내 씀
SPEECH_REGION = config.AZURE_SPEECH_REGION   # 3. '금고'에서 꺼내 씀


# --- 이게 '메인 공장(app.py)'이 호출할 '부품 1 (TTS 엔진)' ---
def speak_text(text_to_speak):
    """
    이 함수를 호출하면, 입력된 텍스트가 
    Azure TTS를 통해 스피커로 재생됩니다.
    """
    
    print(f"[부품 3호 / TTS] 음성 출력 시도: '{text_to_speak[:20]}...'") 
    
    try:
        # 1. Azure 음성 서비스에 접속 설정 (키와 지역 정보 사용)
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        
        # 2. 한국어 목소리 설정 ('SunHi'님)
        speech_config.speech_synthesis_voice_name = "ko-KR-SunHiNeural" 
        
        # 3. 스피커로 바로 출력하도록 설정
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        # 4. Azure 서버에 "이 텍스트 읽어줘!"라고 요청 전송
        result = speech_synthesizer.speak_text_async(text_to_speak).get()
        
        # 5. (혹시 모를 예외 처리)
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"[부품 3호 / 오류!] 음성 변환 실패: {result.reason}")

    except Exception as e:
        print(f"[부품 3호 / 오류!] Azure 음성 서비스 연결 실패: {e}")


# --- (★ 여기가 '새로 조립'한 부품 2 (STT 엔진 - '마이크') ★) ---
def listen_from_mic():
    """
    [STT] 사용자의 마이크 입력을 '한 번' 듣고 '텍스트'로 변환하여 반환합니다.
    """
    print(f"\n[부품 3호 / STT] '마이크'가 켜졌습니다... (말씀하세요)")
    
    try:
        # 1. Azure 음성 서비스에 접속 설정 (TTS랑 똑같음)
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        
        # 2. '한국어'로 인식하도록 설정
        speech_config.speech_recognition_language = "ko-KR"

        # 3. '마이크'를 입력 장치로 사용 설정
        # (특정 오디오 장치를 쓸 수도 있지만, '기본 마이크'로 설정)
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        
        # 4. '음성 인식기' 생성
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # 5. "한 문장"만 인식 (말이 끝나면 자동으로 멈춤)
        # (recognize_once_async()가 '핵심' 부품)
        result = speech_recognizer.recognize_once_async().get()

        # 6. 인식 결과 '판독'
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # (성공!)
            recognized_text = result.text
            print(f"[부품 3호 / STT] 인식 성공: '{recognized_text}'")
            return recognized_text
        
        elif result.reason == speechsdk.ResultReason.NoMatch:
            # (말을 하긴 했는데, '소음'이라서 못 알아들음)
            print("[부품 3호 / STT] 인식 실패: (음성을 인식할 수 없습니다)")
            return None
        
        elif result.reason == speechsdk.ResultReason.Canceled:
            # (마이크가 없거나, '열쇠'가 틀렸거나...)
            print("[부품 3호 / STT] 인식 취소: (마이크 연결 또는 API 키를 확인하세요)")
            return None
            
    except Exception as e:
        print(f"[부품 3호 / 오류!] Azure STT 연결 실패: {e}")
        return None
    

# --- (이 파일 자체를 테스트하기 위한 '시동 장치') ---
if __name__ == "__main__":
    
    print("--- [부품 3호 공장] 자체 테스트 시작 ---")
    
    # --- (테스트 1: '성우' 테스트) ---
    print("\n[테스트 1: '성우' (TTS) 목소리 테스트]")
    test_sentence = "부품 공장 3호, 음성 출력 테스트입니다. 목소리가 들리면 성공입니다."
    speak_text(test_sentence)
    
    # --- (★ 여기가 '새로 추가'된 '마이크' 테스트 ★) ---
    print("\n[테스트 2: '마이크' (STT) 인식 테스트]")
    speak_text("지금부터 '마이크' 테스트를 시작합니다. '안녕하세요'라고 말씀해보세요.")
    
    # '마이크' 부품('귀') 호출!
    user_speech = listen_from_mic()
    
    if user_speech:
        speak_text(f"당신이 방금 '{user_speech}'라고 말했군요. 인식에 성공했습니다.")
    else:
        speak_text("음성을 인식하지 못했습니다. 테스트를 종료합니다.")
    
    print("\n--- [부품 3호 공장] 자체 테스트 종료 ---")