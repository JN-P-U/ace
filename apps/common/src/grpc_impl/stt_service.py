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
        인식 결과를 실시간으로 스트리밍 응답으로 반환합니다.
        """
        # Azure Speech SDK의 PushAudioInputStream 생성
        push_stream = speechsdk.audio.PushAudioInputStream()

        # 새로운 start_continuous_recognition_with_stream()를 사용하여
        # PushAudioInputStream을 오디오 입력으로 지정합니다.
        start_continuous_recognition_with_stream(audio_input_stream=push_stream)

        # gRPC 클라이언트로부터 오디오 청크를 수신하면서, 이를 PushAudioInputStream에 씁니다.
        try:
            for audio_chunk in request_iterator:
                # audio_chunk.data는 gRPC 메시지에 포함된 오디오 데이터(bytes)라고 가정합니다.
                push_stream.write(audio_chunk.data)

                # 인식된 결과가 있다면 바로 yield
                # (stt_result_generator()가 인식된 텍스트를 반환하도록 작성되어 있음)
                for result in stt_result_generator():
                    yield stt_pb2.StreamRecognizedResponse(data=result)
        except Exception as e:
            print("오디오 스트림 처리 중 에러:", e)
        finally:
            push_stream.close()
            stop_continuous_recognition()
