# speech_service.py

import azure.cognitiveservices.speech as speechsdk
import config 

SPEECH_KEY = config.AZURE_SPEECH_KEY
SPEECH_REGION = config.AZURE_SPEECH_REGION

# --- (★ 여기가 '수술'한 '부품 1 (TTS 엔진)') ---
# --- (이름 변경: speak_text -> get_speech_data) ---
def get_speech_data(text_to_speak):
    """
    이 함수를 호출하면, 입력된 텍스트가 
    Azure TTS를 통해 '음성 데이터(bytes)'로 반환됩니다.
    (재생은 안 함!)
    """
    
    print(f"[부품 3호 / TTS] '음성 데이터' 생성 시도: '{text_to_speak[:20]}...'") 
    
    try:
        # 1. Azure 음성 서비스에 접속 설정
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        
        # 2. 한국어 목소리 설정 ('SunHi'님)
        speech_config.speech_synthesis_voice_name = "ko-KR-SunHiNeural" 
        
        # 3. (★ 중요!) '스피커'가 아닌 '메모리'로 받도록 설정
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None) 
        
        # 4. Azure 서버에 "이 텍스트 '데이터'로 줘!"라고 요청
        result = speech_synthesizer.speak_text_async(text_to_speak).get()
        
        # 5. 결과 '판독'
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"[부품 3호 / TTS] '음성 데이터' 생성 성공! ({len(result.audio_data)} 바이트)")
            # (★ 여기가 '핵심'!) '재생'하는 대신 '데이터'를 '반환'
            return result.audio_data
        
        else:
            print(f"[부M 3호 / 오류!] 음성 변환 실패: {result.reason}")
            return None # (실패하면 'None' 반환)

    except Exception as e:
        print(f"[부품 3호 / 오류!] Azure 음성 서비스 연결 실패: {e}")
        return None # (실패하면 'None' 반환)


# --- (★ '부품 2 (STT - 마이크)'는 일단 '그대로' 둠!) ---
# --- (이건 '더 큰 수술'이 필요하니까 나중에!) ---
def listen_from_mic():
    """
    [STT] 사용자의 마이크 입력을 '한 번' 듣고 '텍스트'로 변환하여 반환합니다.
    (주의: 지금 이 코드는 '서버'의 마이크를 쓰려고 해서 배포 시 작동 안 함!)
    """
    print(f"\n[부품 3호 / STT] '마이크'가 켜졌습니다... (말씀하세요)")
    
    try:
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_recognition_language = "ko-KR"
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        result = speech_recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            recognized_text = result.text
            print(f"[부M 3호 / STT] 인식 성공: '{recognized_text}'")
            return recognized_text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("[부품 3호 / STT] 인식 실패: (음성을 인식할 수 없습니다)")
            return None
        elif result.reason == speechsdk.ResultReason.Canceled:
            print("[부품 3호 / STT] 인식 취소: (마이크 연결 또는 API 키를 확인하세요)")
            return None
    except Exception as e:
        print(f"[부품 3호 / 오류!] Azure STT 연결 실패: {e}")
        return None

# --- (이 파일 자체를 테스트하기 위한 '시동 장치') ---
if __name__ == "__main__":
    
    print("--- [부품 3호 공장] 자체 테스트 시작 ---")
    
    # --- (테스트 1: '성우' 테스트) ---
    print("\n[테스트 1: '성우' (TTS) '데이터' 생성 테스트]")
    test_sentence = "부품 3호, '데이터' 생성 테스트입니다. '바이트'가 나오면 성공입니다."
    
    # '데이터'를 받아보자!
    audio_data = get_speech_data(test_sentence)
    
    if audio_data:
        print(f"✅ '음성 데이터'가 정확히 반환되었습니다! (크기: {len(audio_data)} 바이트)")
    else:
        print("❌ '음성 데이터' 생성에 실패했습니다.")
    
    # --- (테스트 2: '마이크' 테스트는 '로컬'에서만 가능) ---
    print("\n[테스트 2: '마이크' (STT) 인식 테스트 (로컬 전용)]")
    
    print("\n--- [부품 3호 공장] 자체 테스트 종료 ---")