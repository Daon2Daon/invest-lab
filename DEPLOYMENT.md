# 배포 가이드

## 서버 배포 준비

### 1. 환경변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```bash
# .env.example을 복사하여 시작
cp .env.example .env
```

**필수 설정:**
```bash
# 관리자 계정 (반드시 변경하세요!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password-here

# 데이터베이스 경로
DATABASE_PATH=./data/portfolios.db

# 포트 설정
HOST_PORT=8501          # 외부에서 접근하는 포트
CONTAINER_PORT=8501     # 컨테이너 내부 포트 (변경 불필요)
```

**선택 설정:**
```bash
# AI 분석 기능 사용 시
GEMINI_API_KEY=your-gemini-api-key

# 보안 설정
MIN_PASSWORD_LENGTH=8
```

### 2. 포트 설정 방법

#### 옵션 1: 환경변수로 설정 (권장)
```bash
# .env 파일에서
HOST_PORT=8080  # 서버에서 8080 포트 사용
```

#### 옵션 2: docker-compose 명령어로 설정
```bash
HOST_PORT=8080 docker-compose up -d
```

#### 옵션 3: docker-compose.yml 파일 직접 수정
```yaml
ports:
  - "8080:8501"  # 호스트:컨테이너
```

### 3. 배포 환경별 실행 방법

#### 프로덕션 환경 (권장)
```bash
docker-compose up -d
```

#### 개발 환경 (코드 실시간 반영)
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 4. 배포 전 체크리스트

- [ ] `.env` 파일 생성 및 관리자 비밀번호 설정
- [ ] `data/` 디렉토리가 `.gitignore`에 포함되어 있는지 확인
- [ ] 서버 방화벽에서 설정한 포트 열기
- [ ] HTTPS 사용 시 리버스 프록시 설정 (nginx 등)

### 5. 데이터 백업

**수동 백업:**
```bash
# 데이터베이스 백업
cp ./data/portfolios.db ./backups/portfolios_$(date +%Y%m%d).db
```

**자동 백업 스크립트:**
```bash
# backup.sh 실행
./backup.sh
```

### 6. 컨테이너 관리

```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs invest-lab-app

# 컨테이너 재시작
docker-compose restart

# 컨테이너 중지 및 제거
docker-compose down
```

### 7. 포트 충돌 해결

8501 포트가 이미 사용 중인 경우:

**방법 1: 다른 포트 사용**
```bash
# .env 파일
HOST_PORT=8080
```

**방법 2: 기존 프로세스 종료**
```bash
# 8501 포트 사용 중인 프로세스 확인
lsof -i :8501

# 프로세스 종료
kill -9 <PID>
```

### 8. HTTPS 설정 (선택)

nginx 리버스 프록시 설정 예시:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 9. 보안 권장사항

1. **관리자 비밀번호 강력하게 설정**
   - 최소 12자 이상
   - 대소문자, 숫자, 특수문자 조합

2. **데이터베이스 파일 권한 설정**
   ```bash
   chmod 600 ./data/portfolios.db
   ```

3. **방화벽 설정**
   - 필요한 포트만 열기
   - SSH 포트 변경 고려

4. **정기 백업**
   - cron으로 자동 백업 설정
   - 백업 파일 암호화 고려

### 10. 문제 해결

**컨테이너가 시작되지 않는 경우:**
```bash
# 로그 확인
docker logs invest-lab-app

# 이미지 재빌드
docker-compose build --no-cache
```

**데이터베이스 초기화:**
```bash
# 주의: 모든 데이터가 삭제됩니다!
rm -rf ./data/portfolios.db
docker-compose restart
```

**포트 변경이 적용되지 않는 경우:**
```bash
# 컨테이너 완전 재생성
docker-compose down
docker-compose up -d
```

## 추가 문서

- [README.md](README.md) - 프로젝트 개요
- [.env.example](.env.example) - 환경변수 템플릿
