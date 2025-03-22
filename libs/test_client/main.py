import grpc
from src.protos import stt_pb2, stt_pb2_grpc


def run():
    # gRPC 채널 생성
    # channel = grpc.insecure_channel("localhost:50051")
    channel = grpc.insecure_channel("mygrpcserver.home:50051")
    stub = stt_pb2_grpc.STTServiceStub(channel)


    # StreamRecognized 호출 및 스트리밍 응답 처리
    for response in stub.StreamRecognized(stt_pb2.StreamRecognizedRequest()):
        print(f"StreamRecognized Response: {response.data}")

    def audio_stream_generator():
        # 예시: 0.1초 간격으로 PCM bytes 청크 전송
        for _ in range(100):
            yield stt_pb2.StreamRecognizedRequest(data=b'\x00\x01\x02\x03' * 1000)
    
    # 서버에 오디오 스트림 요청하고 인식 결과를 스트리밍 받음
    for response in stub.StreamRecognized(audio_stream_generator()):
        print("인식 결과:", response.data)
    # Stop 호출
    # stop_response = stub.Stop(stt_pb2.StopRequest())
    # print(f"Stop Response: {stop_response.message}")
    # print(f"Final Results: {stop_response.results}")


if __name__ == "__main__":
    run()


def run():

    # 오디오 데이터를 스트리밍 요청으로 전송하는 예시 (실제 오디오 데이터로 대체)