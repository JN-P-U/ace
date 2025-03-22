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


def start_continuous_recognition():
    global speech_recognizer, recognition_thread, running
    if running:
        print("이미 인식이 실행 중입니다.")
        return
    running = True

    service_speech_key = speech_key
    service_speech_region = speech_region
    print("service_speech_key : ", service_speech_key)
    print("service_speech_region : ", service_speech_region)
    print("speech_language : ", speech_language)
    speech_config = speechsdk.SpeechConfig(
        subscription=service_speech_key, region=service_speech_region
    )
    speech_config.speech_recognition_language = speech_language

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    # 이벤트 핸들러: 인식 중 및 인식 완료 시 결과 저장
    def recognizing_handler(evt):
        text = evt.result.text
        print("인식 중:", text)
        stt_queue.put(text)

    def recognized_handler(evt):
        text = evt.result.text
        print("인식 완료:", text)
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
    """실시간으로 인식 결과를 SSE 형식으로 반환하는 제너레이터"""
    while running:
        try:
            result = stt_queue.get(timeout=1)
            yield f"data: {result}\n\n"
        except Empty:
            continue
    # 세션 종료 후 최종 메시지 전송
    yield "data: STT session ended\n\n"
