import azure.cognitiveservices.speech as speechsdk
from src.protos import stt_pb2, stt_pb2_grpc
from src.services.recognition import (
    start_continuous_recognition_with_stream,
    stop_continuous_recognition,
    stt_result_generator,
)


class STTServiceServicer(stt_pb2_grpc.STTServiceServicer):
    def StreamRecognized(self, request_iterator, context):
        """
        클라이언트에서 전달받은 오디오 스트림 데이터를 Azure STT에 전달하고,
        인식 결과를 실시간 스트리밍 응답으로 반환합니다.
        이 메서드에서는 별도의 타임아웃 없이, 클라이언트가 모든 오디오 데이터를 전송할 때까지 처리합니다.
        (세션 종료는 클라이언트의 Stop RPC 호출로 처리됩니다.)
        """
        # Azure Speech SDK의 PushAudioInputStream 생성
        push_stream = speechsdk.audio.PushAudioInputStream()

        # start_continuous_recognition_with_stream()를 호출하여
        # 오디오 입력으로 push_stream을 지정하고, Azure STT 인식을 시작합니다.
        start_continuous_recognition_with_stream(audio_input_stream=push_stream)

        try:
            # gRPC 클라이언트로부터 오디오 청크를 수신하며 처리합니다.
            for audio_chunk in request_iterator:
                # audio_chunk.data는 gRPC 메시지 내의 오디오 데이터 (bytes)라고 가정
                push_stream.write(audio_chunk.data)

                # 인식 결과가 있으면, stt_result_generator()를 통해 반환된 결과를 yield합니다.
                for result in stt_result_generator():
                    yield stt_pb2.StreamRecognizedResponse(data=result)
        except Exception as e:
            print("오디오 스트림 처리 중 에러:", e)
        finally:
            push_stream.close()
            # Stop RPC가 별도로 호출되어 stop_continuous_recognition()가 실행됩니다.
            # 필요하다면 남은 결과를 반환할 수 있습니다.
            for result in stt_result_generator():
                yield stt_pb2.StreamRecognizedResponse(data=result)

    def Start(self, request, context):
        """
        별도의 Start RPC 메서드: 기본 마이크 사용 혹은 다른 입력 없이 STT 인식을 시작합니다.
        (필요에 따라 수정)
        """
        start_continuous_recognition_with_stream(audio_input_stream=None)
        return stt_pb2.StartResponse(message="STT started")

    def Stop(self, request, context):
        """
        클라이언트에서 Stop RPC를 호출하면, 이 메서드가 실행되어
        전역 상태를 변경하고 STT 인식을 중지합니다.
        """
        results = stop_continuous_recognition()
        return stt_pb2.StopResponse(message="STT stopped", results=results)
