import grpc
from src.protos import stt_pb2, stt_pb2_grpc


def run():
    # gRPC 채널 생성
    channel = grpc.insecure_channel("localhost:50051")
    stub = stt_pb2_grpc.STTServiceStub(channel)

    # Start 호출
    start_response = stub.Start(stt_pb2.StartRequest())
    print(f"Start Response: {start_response.message}")

    # StreamRecognized 호출 및 스트리밍 응답 처리
    for response in stub.StreamRecognized(stt_pb2.StreamRecognizedRequest()):
        print(f"StreamRecognized Response: {response.data}")

    # Stop 호출
    stop_response = stub.Stop(stt_pb2.StopRequest())
    print(f"Stop Response: {stop_response.message}")
    print(f"Final Results: {stop_response.results}")


if __name__ == "__main__":
    run()
