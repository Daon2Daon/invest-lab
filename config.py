"""애플리케이션 설정 및 상수 정의"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================================================
# 데이터베이스 설정
# ==================================================
DATABASE_PATH = os.environ.get("DATABASE_PATH", "./data/portfolios.db")

# ==================================================
# 인증 설정
# ==================================================
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin1234")
MIN_PASSWORD_LENGTH = int(os.environ.get("MIN_PASSWORD_LENGTH", 8))
BCRYPT_ROUNDS = 12

# ==================================================
# 백테스트 설정
# ==================================================
RISK_FREE_RATE = 3.5  # 무위험 수익률 (%)
TRADING_DAYS_PER_YEAR = 252

# 리밸런싱 옵션
REBALANCE_OPTIONS = ["None", "Yearly", "Semi-Annually", "Quarterly", "Monthly"]

# 벤치마크 옵션
BENCHMARK_MAP = {
    "S&P 500": "SPY",
    "Nasdaq 100": "QQQ",
    "KOSPI": "^KS11",
    "Gold": "GLD"
}

# 자산 유형
ASSET_TYPES = ["Stock", "Bond", "REITs", "Gold/Cmdty", "Cash", "Crypto"]

# ==================================================
# 마켓 설정
# ==================================================
# 시장별 티커 접미사
MARKET_SUFFIXES = {
    "KR_KOSPI": ".KS",
    "KR_KOSDAQ": ".KQ",
    "JP": ".T"
}

# 통화 매핑
CURRENCY_MAP = {
    ".KS": "KRW",
    ".KQ": "KRW",
    ".T": "JPY"
}

# 환율 티커
FX_TICKERS = {
    "USD_KRW": "KRW=X",
    "JPY_KRW": "JPYKRW=X"
}

# KRW 자산 판별을 위한 접미사
KRW_ASSET_SUFFIXES = (".KS", ".KQ")
KRW_ASSET_TICKERS = ("^KS11",)

# ==================================================
# AI 분석 설정
# ==================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3-flash-preview"  # Gemini 3 Flash (미리보기 버전)

# ==================================================
# UI 설정
# ==================================================
DEFAULT_START_YEAR = 2018
WEIGHT_TOLERANCE = 0.1  # 총 비중 100%에서 허용 오차

# 차트 색상
CHART_COLORS = {
    "primary": "#0F172A",
    "benchmark": "#94A3B8",
    "success": "#10B981",
    "error": "#EF4444"
}

# ==================================================
# Technical Analysis 설정
# ==================================================
# EMA 기간 (기본값)
TA_EMA_PERIODS = [20, 50, 200]

# 볼린저 밴드 설정
TA_BB_PERIOD = 20
TA_BB_STD = 2.0

# RSI 설정
TA_RSI_PERIOD = 14

# MACD 설정
TA_MACD_FAST = 12
TA_MACD_SLOW = 26
TA_MACD_SIGNAL = 9

# 타임프레임 매핑
TA_TIMEFRAME_MAP = {
    "Daily": "1d",
    "Weekly": "1wk",
    "Monthly": "1mo"
}

# 데이터 기간 매핑
TA_PERIOD_MAP = {
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}

# EMA 색상
TA_EMA_COLORS = {
    20: "#EF4444",   # Red
    50: "#F97316",   # Orange
    200: "#EAB308"   # Dark Yellow
}
