# 실행 방법(mac)

1. python3.11 설치
- brew install python@3.11

2. pipx 설치
- brew install pipx
- pipx ensurepath
    - pipx의 실행 경로를 셸 환경 변수에 추가
    - 터미널 재실행

3. poetry 설치
- pipx install pipx
- poetry --version

4. python3.11로 가상환경 생성
- poetry env use python3.11

5. 가상환경 실행
- 실행 대상 서비스 진입
  ex :  cd apps/common
- 실행 : source $(poetry env info --path)/bin/activate

6. 의존성 설치
- poetry install

7. 서버 실행
- 로컬 실행 시 : ENV_FILE=.env.local poetry run python main.py
- 개발 실행 시 : poetry run python main.py

