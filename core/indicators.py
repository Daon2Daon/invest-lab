"""기술적 지표 계산 모듈"""

import pandas as pd
import numpy as np

from config import (
    TA_EMA_PERIODS,
    TA_BB_PERIOD,
    TA_BB_STD,
    TA_RSI_PERIOD,
    TA_MACD_FAST,
    TA_MACD_SLOW,
    TA_MACD_SIGNAL
)


def calculate_ema(data: pd.Series, periods: list[int] = None) -> dict[int, pd.Series]:
    """
    지수이동평균(EMA) 계산

    Args:
        data: Close 가격 시리즈
        periods: EMA 기간 리스트 (기본: config의 TA_EMA_PERIODS)

    Returns:
        dict: {기간: EMA 시리즈}
    """
    if periods is None:
        periods = TA_EMA_PERIODS

    return {period: data.ewm(span=period, adjust=False).mean() for period in periods}


def calculate_bollinger_bands(
    data: pd.Series,
    period: int = None,
    std_dev: float = None
) -> dict[str, pd.Series]:
    """
    볼린저 밴드 계산

    Args:
        data: Close 가격 시리즈
        period: 이동평균 기간 (기본: config의 TA_BB_PERIOD)
        std_dev: 표준편차 배수 (기본: config의 TA_BB_STD)

    Returns:
        dict: {"upper": Series, "middle": Series, "lower": Series}
    """
    if period is None:
        period = TA_BB_PERIOD
    if std_dev is None:
        std_dev = TA_BB_STD

    middle = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()

    return {
        "upper": middle + (std * std_dev),
        "middle": middle,
        "lower": middle - (std * std_dev)
    }


def calculate_rsi(data: pd.Series, period: int = None) -> pd.Series:
    """
    RSI (Relative Strength Index) 계산

    Args:
        data: Close 가격 시리즈
        period: RSI 기간 (기본: config의 TA_RSI_PERIOD)

    Returns:
        RSI 시리즈 (0-100)
    """
    if period is None:
        period = TA_RSI_PERIOD

    delta = data.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(
    data: pd.Series,
    fast: int = None,
    slow: int = None,
    signal: int = None
) -> dict[str, pd.Series]:
    """
    MACD 계산

    Args:
        data: Close 가격 시리즈
        fast: 빠른 EMA 기간 (기본: config의 TA_MACD_FAST)
        slow: 느린 EMA 기간 (기본: config의 TA_MACD_SLOW)
        signal: 시그널 라인 기간 (기본: config의 TA_MACD_SIGNAL)

    Returns:
        dict: {"macd": Series, "signal": Series, "histogram": Series}
    """
    if fast is None:
        fast = TA_MACD_FAST
    if slow is None:
        slow = TA_MACD_SLOW
    if signal is None:
        signal = TA_MACD_SIGNAL

    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()

    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": macd_line - signal_line
    }


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """
    VWAP (Volume Weighted Average Price) 계산

    Args:
        df: OHLCV DataFrame (High, Low, Close, Volume 컬럼 필요)

    Returns:
        VWAP 시리즈
    """
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    cumulative_tp_vol = (typical_price * df['Volume']).cumsum()
    cumulative_vol = df['Volume'].cumsum()

    # 0으로 나누기 방지
    vwap = cumulative_tp_vol / cumulative_vol.replace(0, np.nan)

    return vwap
