# from src.protos import stt_pb2, stt_pb2_grpc
# from src.services.recognition import (
#     start_continuous_recognition,
#     stop_continuous_recognition,
#     stt_result_generator,
# )


# class STTServiceServicer(stt_pb2_grpc.STTServiceServicer):
#     def Start(self, request, context):
#         start_continuous_recognition()
#         return stt_pb2.StartResponse(message="STT started")

#     def Stop(self, request, context):
#         results = stop_continuous_recognition()
#         return stt_pb2.StopResponse(message="STT stopped", results=results)

#     def StreamRecognized(self, request, context):
#         # recognition.py의 stt_result_generator()를 이용해 서버->클라이언트 스트리밍
#         for data in stt_result_generator():
#             yield stt_pb2.StreamRecognizedResponse(data=data)

import threading
import time

import azure.cognitiveservices.speech as speechsdk
from src.protos import stt_pb2, stt_pb2_grpc
from src.services.recognition import (
    start_continuous_recognition,
    stop_continuous_recognition,
    stt_result_generator,
)


class STTServiceServicer(stt_pb2_grpc.STTServiceServicer):
    def StreamRecognized(self, request_iterator, context):
        """
        클라이언트에서 전달받은 오디오 스트림 데이터를 Azure STT로 실시간 인식하고,
        인식된 텍스트를 스트리밍 응답으로 반환합니다.
        """

        # Azure Speech SDK의 푸시 스트림 생성: 오디오 데이터를 직접 전달할 스트림입니다.
        push_stream = speechsdk.audio.PushAudioInputStream()

        # 위 푸시 스트림을 사용하여 AudioConfig 생성
        audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

        # Azure Speech 서비스 설정 (구독키, 리전을 실제 값으로 설정)
        speech_config = speechsdk.SpeechConfig(
            subscription="YourAzureSubscriptionKey", region="YourRegion"
        )

        # SpeechRecognizer 생성: 오디오 입력은 push_stream에서 가져옵니다.
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        # 인식 결과를 저장할 리스트와 동기화를 위한 Lock
        recognized_results = []
        lock = threading.Lock()

        # 인식 콜백 함수: 인식된 텍스트를 리스트에 저장합니다.
        def recognized_cb(evt):
            with lock:
                recognized_results.append(evt.result.text)

        recognizer.recognized.connect(recognized_cb)

        # 연속 인식 시작 (비동기)
        recognizer.start_continuous_recognition()

        # gRPC 클라이언트에서 오디오 청크를 수신하면서, Azure로 전달
        try:
            for audio_chunk in request_iterator:
                # audio_chunk.data는 gRPC 메시지 내에 있는 바이트 데이터라고 가정합니다.
                push_stream.write(audio_chunk.data)

                # 인식 결과가 있다면, yield로 즉시 클라이언트에 응답
                with lock:
                    while recognized_results:
                        text = recognized_results.pop(0)
                        yield stt_pb2.StreamRecognizedResponse(data=text)
        except Exception as e:
            print("오디오 스트림 처리 중 에러:", e)
        finally:
            # 오디오 입력 종료를 알림
            push_stream.close()
            # 추가로 잠시 대기하여 마지막 결과를 수집 (필요한 경우)
            time.sleep(2)
            recognizer.stop_continuous_recognition()

            with lock:
                while recognized_results:
                    text = recognized_results.pop(0)
                    yield stt_pb2.StreamRecognizedResponse(data=text)
