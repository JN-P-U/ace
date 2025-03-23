import os
import queue
import threading
import time
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from src.protos import stt_pb2, stt_pb2_grpc

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

print("speech_key :", speech_key)
print("speech_region :", speech_region)
print("speech_language :", speech_language)

# FINAL_RESULTS는 최종 인식(RecognizedSpeech) 이벤트에서 나온 전체 문장들을 누적합니다.
FINAL_RESULTS = []


class AzureSTTClient:
    def __init__(self):
        self.push_stream = speechsdk.audio.PushAudioInputStream()
        # 실제 Azure STT 구독 정보로 교체하세요.
        self.speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, region=speech_region
        )
        self.speech_config.speech_recognition_language = speech_language
        self.audio_config = speechsdk.audio.AudioConfig(stream=self.push_stream)
        self.recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, audio_config=self.audio_config
        )
        self.results_queue = queue.Queue()

        # 등록된 이벤트 핸들러:
        # Interim(인식 중) 결과는 (False, text) 형식,
        # 최종(Final) 결과는 (True, text) 형식으로 큐에 넣습니다.
        self.recognizer.recognizing.connect(self._recognizing_handler)
        self.recognizer.recognized.connect(self._recognized_handler)
        self.recognizer.start_continuous_recognition_async()

    def _recognizing_handler(self, evt):
        # 인식 중 결과는 클라이언트에 실시간으로 전달하지만,
        # 최종 결과에 누적하지 않습니다.
        self.results_queue.put((False, evt.result.text))

    def _recognized_handler(self, evt):
        # 최종 인식 결과일 경우에만 True로 표시하고, 큐에 넣습니다.
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            self.results_queue.put((True, evt.result.text))

    def write(self, data):
        self.push_stream.write(data)

    def get_result(self):
        try:
            return self.results_queue.get_nowait()
        except queue.Empty:
            return None

    def close(self):
        self.recognizer.stop_continuous_recognition_async()
        self.push_stream.close()


class STTServiceServicer(stt_pb2_grpc.STTServiceServicer):
    def StreamRecognized(self, request_iterator, context):
        """
        클라이언트에서 전달받은 오디오 스트림 데이터를 Azure STT로 전달하고,
        인식 결과(Interim 및 Final)를 실시간 스트리밍 응답으로 반환합니다.
        이때, 최종 인식 결과만 FINAL_RESULTS에 누적합니다.
        """
        azure_client = AzureSTTClient()

        try:
            for audio_chunk in request_iterator:
                # 클라이언트에서 받은 오디오 데이터를 AzureSTTClient에 전달
                azure_client.write(audio_chunk.data)

                # 바로 인식 결과를 폴링하여 반환 (blocking 없이)
                result = azure_client.get_result()
                if result:
                    is_final, text = result
                    # 최종 인식 결과일 경우에만 누적합니다.
                    if is_final:
                        FINAL_RESULTS.append(text)
                    yield stt_pb2.StreamRecognizedResponse(data=text)
        except Exception as e:
            print("오디오 스트림 처리 중 에러:", e)
        finally:
            azure_client.close()
            # 남은 결과들을 플러시하여 반환합니다.
            while True:
                result = azure_client.get_result()
                if result:
                    is_final, text = result
                    if is_final:
                        FINAL_RESULTS.append(text)
                    yield stt_pb2.StreamRecognizedResponse(data=text)
                else:
                    break

    def Start(self, request, context):
        """
        별도의 Start RPC 메서드: 기본 마이크 사용 혹은 다른 입력 없이 STT 인식을 시작합니다.
        (필요에 따라 수정)
        """
        return stt_pb2.StartResponse(message="STT started")

    def Stop(self, request, context):
        """
        클라이언트에서 Stop RPC를 호출하면, 이 메서드가 실행되어
        STT 인식을 중지하고, 최종 인식 결과들만 반환합니다.
        최종 인식 결과는 각 문장별로 배열에 담아 반환합니다.
        """
        # time.sleep(1)
        global FINAL_RESULTS
        result_text = FINAL_RESULTS.copy()
        print("result_text :", result_text)
        FINAL_RESULTS = []
        # 여기서는 join이나 분리자가 아닌, 최종 결과 리스트 자체를 반환합니다.
        return stt_pb2.StopResponse(message="STT stopped", results=result_text)
