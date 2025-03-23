# src/recognition/main.py
import os
import threading
import time
from pathlib import Path
from queue import Empty, Queue

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# .env 파일 로드
PROJECT_ROOT = Path(__file__).resolve().parents[2]

env_path = PROJECT_ROOT / "conf/"
if os.getenv("env", "").lower() == "local":
    env_path = env_path / ".env.local"
else:
    env_path = env_path / ".env"

load_dotenv(env_path)
# print("env_path : ", env_path)

# 전역 변수: 현재 STT 상태와 관련 객체들을 저장
speech_key = os.getenv("SPEECH_KEY")
speech_region = os.getenv("SPEECH_REGION")
speech_language = os.getenv("SPEECH_LANGUAGE")

running = False
stt_queue = Queue()
stt_results = []


def start_continuous_recognition_with_stream(audio_input_stream=None):
    """음성 인식을 시작합니다. audio_input_stream이 제공되면 이를 사용하고,
    그렇지 않으면 기본 마이크를 사용합니다."""
    global speech_recognizer, recognition_thread, running
    if running:
        print("이미 인식이 실행 중입니다.")
        return
    running = True

    service_speech_key = speech_key
    service_speech_region = speech_region
    print("service_speech_key :", service_speech_key)
    print("service_speech_region :", service_speech_region)
    print("speech_language :", speech_language)
    speech_config = speechsdk.SpeechConfig(
        subscription=service_speech_key, region=service_speech_region
    )
    speech_config.speech_recognition_language = speech_language

    if audio_input_stream is None:
        # 기본 마이크 입력 사용
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    else:
        # 외부에서 제공한 audio_input_stream 사용
        audio_config = speechsdk.audio.AudioConfig(stream=audio_input_stream)

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    def recognizing_handler(evt):
        text = evt.result.text
        print("인식 중:", text)
        stt_queue.put(text)

    def recognized_handler(evt):
        text = evt.result.text
        print("인식 완료 (콜백):", text)
        stt_queue.put(text)
        stt_results.append(text)

    def session_started_handler(evt):
        print("세션 시작")

    def session_stopped_handler(evt):
        print("세션 종료")

    def canceled_handler(evt):
        print("취소됨:", evt.reason, evt.error_details)

    speech_recognizer.recognizing.connect(recognizing_handler)
    speech_recognizer.recognized.connect(recognized_handler)
    speech_recognizer.session_started.connect(session_started_handler)
    speech_recognizer.session_stopped.connect(session_stopped_handler)
    speech_recognizer.canceled.connect(canceled_handler)

    def recognition_loop():
        speech_recognizer.start_continuous_recognition()
        print("STT 인식 시작됨.")
        while running:
            time.sleep(0.5)
        speech_recognizer.stop_continuous_recognition()
        print("STT 인식 종료됨.")

    recognition_thread = threading.Thread(target=recognition_loop, daemon=True)
    recognition_thread.start()


# 기존 stop_continuous_recognition()와 stt_result_generator() 함수는 그대로 둡니다.
def stop_continuous_recognition():
    global running, recognition_thread, stt_results
    if not running:
        print("실행 중인 인식이 없습니다.")
        return stt_results
    running = False
    if recognition_thread:
        recognition_thread.join(timeout=5)
        print("인식 스레드 종료됨.")
    return stt_results


def stt_result_generator():
    """실시간으로 인식 결과를 반환하는 제너레이터"""
    while running:
        try:
            result = stt_queue.get(timeout=1)
            yield result  # 필요에 따라 SSE 형식으로 가공할 수 있음
        except Empty:
            continue
    yield "STT session ended"
