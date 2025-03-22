# 실행 방법(mac)

1. python3.11 설치

- brew install python@3.11

2. pipx 설치

- brew install pipx
- pipx ensurepath
  - pipx의 실행 경로를 셸 환경 변수에 추가
  - 터미널 재실행

3. poetry 설치

- pipx install poetry
- 환경 변수(~/.zshrc)에 poetry directory 추가
  - export PATH="$HOME/.local/bin:$PATH"
  - source ~/.zshrc
- poetry --version

4. python3.11로 가상환경 생성

- poetry env use python3.11

5. 가상환경 실행

- 실행 대상 서비스 진입
  ex : cd apps/common

- 실행1(최초) : chmod +x activate_poetry.sh
- 실행2 : source ./activate_poetry.sh

6. 의존성 설치

- poetry install

7. 서버 실행

- 로컬 실행 시 : env=local poetry run python main.py
- 개발 실행 시 : poetry run python main.py

8. gRPC 서버 실행

- gRPC 의존성 설치: 
  - poetry add grpcio grpcio-tools

- gRPC 프로토콜 버퍼 컴파일 (필요한 경우):
  - 예: poetry run python -m grpc_tools.protoc -I./protos --python_out=./apps/common/src/app --grpc_python_out=./apps/common/src/app ./protos/your_service.proto

- 로컬 실행 시: 
  - env=local poetry run python grpc_server.py

- 개발 실행 시: 
  - poetry run python grpc_server.py

※ grpc_server.py 파일은 gRPC 서버 로직이 포함된 실행 스크립트입니다.
