import threading
import time

import grpc
import pyaudio
from src.protos import stt_pb2, stt_pb2_grpc

# 오디오 캡처 설정
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
FRAMES_PER_BUFFER = 512


def audio_stream_generator(stop_event):
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
    )
    print("오디오 캡처 시작됨.")
    with open("captured_audio.pcm", "wb") as f:
        try:
            while not stop_event.is_set():
                data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                f.write(data)  # PCM 파일에 기록
                yield stt_pb2.StreamRecognizedRequest(data=data)
        except Exception as e:
            print("오디오 캡처 에러:", e)
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
            print("오디오 캡처 종료됨.")


def convert_pcm_to_wav(
    pcm_filepath, wav_filepath, sample_rate=16000, channels=1, sampwidth=2
):
    import wave

    with open(pcm_filepath, "rb") as pcm_file:
        pcm_data = pcm_file.read()
    with wave.open(wav_filepath, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    print(f"변환 완료: {wav_filepath}")


def run():
    channel = grpc.insecure_channel("localhost:50051")
    # channel = grpc.insecure_channel("mygrpcserver.home:50051")
    stub = stt_pb2_grpc.STTServiceStub(channel)
    stop_event = threading.Event()

    # 10초 후에 Stop RPC를 호출하는 백그라운드 스레드
    # def call_stop_after_delay():
    #     time.sleep(10)
    #     stop_event.set()
    #     stop_response = stub.Stop(stt_pb2.StopRequest())
    #     print("Stop Response:", stop_response.message)
    #     print("Final Results:", stop_response.results)
    def call_stop_after_delay():
        time.sleep(10)
        stop_event.set()
        # 별도의 채널 생성
        stop_channel = grpc.insecure_channel("localhost:50051")
        print("Stop Channel:", stop_channel)
        stop_stub = stt_pb2_grpc.STTServiceStub(stop_channel)
        print("Stop Request")
        stop_response = stop_stub.Stop(stt_pb2.StopRequest())
        print("Stop Response:", stop_response)
        print("Stop Response:", stop_response.message)
        print("Final Results:", stop_response.results)

    threading.Thread(target=call_stop_after_delay, daemon=True).start()

    # gRPC로 오디오 스트림 전송 및 서버 응답 처리
    responses = stub.StreamRecognized(audio_stream_generator(stop_event))
    for response in responses:
        print("StreamRecognized Response:", response.data)

    # 오디오 캡처 종료 후, PCM 파일을 WAV 파일로 변환
    convert_pcm_to_wav("captured_audio.pcm", "captured_audio.wav")


if __name__ == "__main__":
    run()
