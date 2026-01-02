"""데이터 수집 모듈"""

import streamlit as st
import yfinance as yf
import pandas as pd
import logging

from config import FX_TICKERS, MARKET_SUFFIXES, CURRENCY_MAP

logger = logging.getLogger(__name__)


def search_ticker(keyword):
    """
    키워드로 티커 검색

    Args:
        keyword: 검색할 티커 키워드 (예: AAPL, 005930)

    Returns:
        tuple: (found, ticker, name, currency)
    """
    keyword = keyword.upper().strip()
    candidates = [keyword]

    # 숫자로만 이루어진 경우 한국/일본 시장 검색
    if keyword.isdigit():
        if len(keyword) == 6:
            # 한국 시장 (KOSPI, KOSDAQ)
            candidates = [
                keyword + MARKET_SUFFIXES["KR_KOSPI"],
                keyword + MARKET_SUFFIXES["KR_KOSDAQ"]
            ]
        elif len(keyword) == 4:
            # 일본 시장
            candidates = [keyword + MARKET_SUFFIXES["JP"]]

    for ticker_symbol in candidates:
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period='1d')

            if not hist.empty:
                name = ticker.info.get('shortName', ticker_symbol)

                # 통화 결정
                currency = "USD"  # 기본값
                for suffix, curr in CURRENCY_MAP.items():
                    if ticker_symbol.endswith(suffix):
                        currency = curr
                        break

                return True, ticker_symbol, name, currency

        except Exception as e:
            logger.debug(f"Ticker search failed for {ticker_symbol}: {e}")
            continue

    return False, None, None, "USD"


def search_by_keyword(keyword: str, limit: int = 5) -> list:
    """
    yfinance Search를 사용하여 종목명/키워드로 검색

    Args:
        keyword: 검색 키워드 (예: cswind, 삼성전자)
        limit: 최대 결과 수

    Returns:
        list: [{'ticker': str, 'name': str, 'currency': str}, ...]
    """
    results = []

    try:
        search = yf.Search(keyword, max_results=limit)

        # quotes 결과에서 종목 정보 추출
        if hasattr(search, 'quotes') and search.quotes:
            for quote in search.quotes[:limit]:
                ticker_symbol = quote.get('symbol', '')
                name = quote.get('shortname') or quote.get('longname', ticker_symbol)

                # 통화 결정
                currency = "USD"  # 기본값
                for suffix, curr in CURRENCY_MAP.items():
                    if ticker_symbol.endswith(suffix):
                        currency = curr
                        break

                results.append({
                    'ticker': ticker_symbol,
                    'name': name,
                    'currency': currency
                })

    except Exception as e:
        logger.debug(f"yfinance search failed for '{keyword}': {e}")

    return results


@st.cache_data(show_spinner=False)
def fetch_data_robust(tickers, benchmark_ticker, start_date, end_date):
    """
    여러 티커의 데이터를 가져옴

    Args:
        tickers: 포트폴리오 티커 리스트
        benchmark_ticker: 벤치마크 티커
        start_date: 시작 날짜
        end_date: 종료 날짜

    Returns:
        DataFrame: 티커별 종가 데이터
    """
    data_dict = {}

    # 환율 티커 포함
    unique_tickers = list(set(
        tickers +
        [benchmark_ticker] +
        [FX_TICKERS["USD_KRW"], FX_TICKERS["JPY_KRW"]]
    ))

    progress_bar = st.progress(0)

    for i, ticker_symbol in enumerate(unique_tickers):
        try:
            ticker_obj = yf.Ticker(ticker_symbol)
            df = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)

            if not df.empty:
                df.index = df.index.tz_localize(None)
                series = df['Close']

                if isinstance(series, pd.Series) and not series.empty:
                    data_dict[ticker_symbol] = series

        except Exception as e:
            logger.warning(f"Failed to fetch data for {ticker_symbol}: {e}")

        progress_bar.progress((i + 1) / len(unique_tickers))

    progress_bar.empty()

    if not data_dict:
        return None

    try:
        combined_df = pd.DataFrame(data_dict)
        return combined_df.ffill().dropna()
    except ValueError as e:
        logger.error(f"Failed to combine data: {e}")
        return None


@st.cache_data(show_spinner=False, ttl=300)
def fetch_ohlcv_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    단일 티커의 OHLCV 데이터 수집 (Technical Analysis용)

    Args:
        ticker: 티커 심볼
        period: 데이터 기간 ("6mo", "1y", "2y", "5y")
        interval: 데이터 간격 ("1d", "1wk", "1mo")

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume (index: Date)
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period, interval=interval, auto_adjust=True)

        if df.empty:
            logger.warning(f"No OHLCV data for {ticker}")
            return None

        # timezone 정보 제거
        df.index = df.index.tz_localize(None)

        # 필요한 컬럼만 선택
        ohlcv_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df[ohlcv_columns]

        # 결측값 처리
        df = df.ffill().dropna()

        return df

    except Exception as e:
        logger.error(f"Failed to fetch OHLCV data for {ticker}: {e}")
        return None
