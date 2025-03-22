from src.protos import stt_pb2, stt_pb2_grpc
from src.services.recognition import (
    start_continuous_recognition,
    stop_continuous_recognition,
    stt_result_generator,
)


class STTServiceServicer(stt_pb2_grpc.STTServiceServicer):
    def Start(self, request, context):
        start_continuous_recognition()
        return stt_pb2.StartResponse(message="STT started")

    def Stop(self, request, context):
        results = stop_continuous_recognition()
        return stt_pb2.StopResponse(message="STT stopped", results=results)

    def StreamRecognized(self, request, context):
        # recognition.py의 stt_result_generator()를 이용해 서버->클라이언트 스트리밍
        for data in stt_result_generator():
            yield stt_pb2.StreamRecognizedResponse(data=data)
