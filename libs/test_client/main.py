import threading
import time

import grpc
from src.protos import stt_pb2, stt_pb2_grpc

SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
FRAMES_PER_BUFFER = 1024


def audio_stream_generator(stop_event):
    # PyAudio 인스턴스 생성
    audio = pyaudio.PyAudio()
    # 마이크 입력 스트림 열기 (PCM 데이터, 16kHz, mono)
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
    )
    print("오디오 캡처 시작됨.")
    try:
        while not stop_event.is_set():
            # 마이크로부터 오디오 데이터를 읽음
            data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
            # 오디오 데이터를 gRPC 메시지로 생성하여 yield
            yield stt_pb2.StreamRecognizedRequest(data=data)
    except Exception as e:
        print("오디오 캡처 에러:", e)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("오디오 캡처 종료됨.")


def run():
    # gRPC 채널 생성 (서버 주소: 예시로 localhost 사용; 실제 환경에 맞게 변경)
    channel = grpc.insecure_channel("localhost:50051")
    stub = stt_pb2_grpc.STTServiceStub(channel)

    # 스트리밍 중단을 위한 이벤트 객체
    stop_event = threading.Event()

    # 10초 후에 Stop RPC를 호출하는 백그라운드 스레드
    def call_stop_after_delay():
        time.sleep(10)
        stop_event.set()  # 제너레이터에 종료 신호 전달
        stop_response = stub.Stop(stt_pb2.StopRequest())
        print("Stop Response:", stop_response.message)
        print("Final Results:", stop_response.results)

    threading.Thread(target=call_stop_after_delay, daemon=True).start()

    # 오디오 스트림 요청을 보내고, 서버로부터 스트리밍 응답 처리
    responses = stub.StreamRecognized(audio_stream_generator(stop_event))
    for response in responses:
        print("StreamRecognized Response:", response.data)


if __name__ == "__main__":
    run()
