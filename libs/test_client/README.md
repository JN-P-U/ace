1. proto 파일 컴파일(제공 하는 쪽으로부터 전달 받아야함)
poetry run python -m grpc_tools.protoc -I ./src/protos --python_out=./src/protos --grpc_python_out=./src/protos ./src/protos/stt.proto

2. 경로 수정
- 대상 파일 : ./src/protos/stt_pb2_grpc.py
- 수정 대상 : import stt_pb2 as stt__pb2
    - 수정 : from src.protos import stt_pb2 as stt__pb2