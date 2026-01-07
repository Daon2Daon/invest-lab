# 1. 가볍고 안정적인 파이썬 3.10 버전 사용
FROM python:3.10-slim

# 2. 타임존 설정 (한국 시간) - 로그 확인 시 편리함
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 3. curl 설치 (healthcheck용)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 4. 작업 폴더 설정
WORKDIR /app

# 5. 필수 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. 소스 코드 복사
COPY . .

# 7. 포트 개방 및 실행
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]