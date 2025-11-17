import os
from typing import Optional

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    raise RuntimeError("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION must be set.")


def synthesize_speech(text: str, voice: str = "ko-KR-SunHiNeural") -> Optional[bytes]:
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION,
        )
        speech_config.speech_synthesis_voice_name = voice
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None,
        )
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        print(f"[tts_service] Speech synthesis failed: {result.reason}")
        return None
    except Exception as exc:
        print(f"[tts_service] Speech synthesis error: {exc}")
        return None

