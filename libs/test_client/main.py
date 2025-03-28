import json
import os
import threading
import time
from datetime import datetime

import grpc
import pyaudio
from src.protos import stt_pb2, stt_pb2_grpc

# 오디오 캡처 설정
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
FRAMES_PER_BUFFER = 512

# server_address = "localhost:50051"
server_address = "mygrpcserver.home:50051"


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
    channel = grpc.insecure_channel(server_address)
    stub = stt_pb2_grpc.STTServiceStub(channel)
    stop_event = threading.Event()

    def call_stop_after_delay():
        time.sleep(10)
        stop_event.set()
        # 별도의 채널 생성
        stop_channel = grpc.insecure_channel(server_address)
        print("Stop Channel:", stop_channel)
        stop_stub = stt_pb2_grpc.STTServiceStub(stop_channel)
        print("Stop Request")
        stop_response = stop_stub.Stop(stt_pb2.StopRequest())
        print("Stop Response:", stop_response)
        print("Stop Response:", stop_response.message)
        print("Final Results:", stop_response.results)
        # 결과 파일 생성
        result_folder = "result"
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(result_folder, f"result_{timestamp}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(list(stop_response.results), f, ensure_ascii=False, indent=4)
        print("Result saved to", file_path)

    threading.Thread(target=call_stop_after_delay, daemon=True).start()

    responses = stub.StreamRecognized(audio_stream_generator(stop_event))
    for response in responses:
        print("StreamRecognized Response:", response.data)

    convert_pcm_to_wav("captured_audio.pcm", "captured_audio.wav")


if __name__ == "__main__":
    run()
