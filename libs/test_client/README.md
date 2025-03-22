1. proto 파일 컴파일(제공 하는 쪽으로부터 전달 받아야함)
poetry run python -m grpc_tools.protoc -I ./src/protos --python_out=./src/protos --grpc_python_out=./src/protos ./src/protos/stt.proto