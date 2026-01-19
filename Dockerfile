# 1. 파이썬 3.11이 설치된 가벼운 리눅스 이미지를 사용함
FROM python:3.11-slim

# 2. 컨테이너 내부의 작업 디렉토리를 /app으로 설정
WORKDIR /app

# 3. 현재 폴더의 모든 파일을 컨테이너 안의 /app으로 복사
COPY . /app

# 4. 필요한 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로그램 실행 (터미널에서 질문을 받아야 하므로 -u 옵션 추가)
CMD ["python", "-u", "app.py"]