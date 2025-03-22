import signal
from concurrent import futures
from multiprocessing import Process

import grpc
import uvicorn
from src.grpc_impl.stt_service import STTServiceServicer
from src.protos import stt_pb2_grpc


def rest_server():
    uvicorn.run("src.apis:app", host="127.0.0.1", port=4900, reload=False)


def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stt_pb2_grpc.add_STTServiceServicer_to_server(STTServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC 서버가 50051 포트에서 실행 중...")
    server.wait_for_termination()


if __name__ == "__main__":
    rest_process = Process(target=rest_server)
    grpc_process = Process(target=grpc_server)
    rest_process.start()
    grpc_process.start()

    def terminate_processes(signum, frame):
        print("프로세스 종료 시작")
        rest_process.terminate()
        grpc_process.terminate()
        rest_process.join()
        grpc_process.join()
        print("프로세스 종료 완료")
        exit(0)

    signal.signal(signal.SIGINT, terminate_processes)
    signal.signal(signal.SIGTERM, terminate_processes)

    try:
        rest_process.join()
        grpc_process.join()
    except KeyboardInterrupt:
        terminate_processes(None, None)
