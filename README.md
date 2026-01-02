# Invest Lab

포트폴리오 백테스팅 및 기술적 분석 도구

## 주요 기능

### 1. Portfolio Backtest
- 다중 자산 포트폴리오 백테스팅
- 리밸런싱 전략 시뮬레이션 (월간/분기/반기/연간)
- 벤치마크 대비 성과 분석
- 주요 성과 지표 계산 (CAGR, MDD, Sharpe Ratio 등)
- AI 기반 포트폴리오 분석 (Google Gemini)

### 2. Technical Analysis
- 실시간 차트 분석 (캔들스틱, 거래량)
- 기술적 지표:
  - EMA (20, 50, 200)
  - Bollinger Bands
  - RSI
  - MACD
  - VWAP
- 다양한 타임프레임 (1분, 5분, 15분, 30분, 1시간, 일봉, 주봉, 월봉)
- 고화질 차트 캡처 기능

### 3. 사용자 관리
- 다중 사용자 인증 시스템
- 개인별 포트폴리오 전략 저장
- 관심종목 관리 (Watchlist)
- 비밀번호 변경 기능
- 관리자 패널

## 빠른 시작

### 사전 요구사항
- Docker & Docker Compose
- (선택) Google Gemini API Key

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 수정 (필수)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

### 2. 실행

**프로덕션 환경 (권장):**
```bash
docker-compose up -d
```

**개발 환경 (코드 변경 시 자동 반영):**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 3. 접속

브라우저에서 `http://localhost:8501` 접속

## 기술 스택

- **Frontend/Backend**: Streamlit + Python
- **Database**: SQLite
- **Data Source**: yfinance
- **Visualization**: Plotly, Matplotlib
- **AI**: Google Gemini API
- **Authentication**: bcrypt
- **Deployment**: Docker

## 프로젝트 구조

```
invest-lab/
├── app.py                 # 메인 애플리케이션
├── config.py              # 설정 파일
├── requirements.txt       # Python 패키지
├── Dockerfile            # Docker 이미지 빌드
├── docker-compose.yml    # 프로덕션 배포 설정
├── docker-compose.dev.yml   # 개발 환경 설정
├── auth/                 # 인증 모듈
├── core/                 # 백테스트 엔진
├── db/                   # 데이터베이스 모델
├── ui/                   # UI 컴포넌트
├── utils/                # 유틸리티
└── data/                 # 데이터베이스 (git 제외)
```

## 보안

- bcrypt 해시 기반 비밀번호 암호화
- 사용자별 데이터 격리 (user_id 기반)
- SQLite 파라미터 바인딩 (SQL Injection 방지)
- 환경변수 기반 민감 정보 관리
- 비밀번호 변경 기능

## 지원 마켓

- 미국 (NYSE, NASDAQ)
- 한국 (KOSPI, KOSDAQ)
- 일본 (도쿄 증권거래소)
- 글로벌 ETF
- 암호화폐

## 배포

자세한 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md) 참고

**포트 변경:**
```bash
# .env 파일에서
HOST_PORT=8080
```

## 라이선스

이 프로젝트는 개인 및 교육 목적으로 사용할 수 있습니다.

## 기여

버그 리포트 및 기능 제안은 Issues를 통해 제출해주세요.

## 면책 조항

이 도구는 교육 및 연구 목적으로 제공됩니다. 실제 투자 결정에 사용하기 전에 전문가와 상담하세요. 과거 성과가 미래 수익을 보장하지 않습니다.

## 문의

프로젝트 관련 문의사항이 있으시면 Issues를 통해 연락 주세요.
