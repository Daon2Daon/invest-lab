# 1. 가볍고 안정적인 파이썬 3.10 버전 사용
FROM python:3.10-slim

# 2. 타임존 설정 (한국 시간) - 로그 확인 시 편리함
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 3. 작업 폴더 설정
WORKDIR /app

# 4. 필수 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 포트 개방 및 실행
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]