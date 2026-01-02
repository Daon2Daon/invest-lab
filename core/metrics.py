"""성과 지표 계산 모듈"""

import numpy as np

from config import RISK_FREE_RATE, TRADING_DAYS_PER_YEAR


def calculate_metrics(daily_ret_series, final_val, start_date, end_date):
    """
    투자 성과 지표 계산

    Args:
        daily_ret_series: 일별 수익률 시리즈
        final_val: 최종 가치 (시작 100 기준)
        start_date: 시작 날짜
        end_date: 종료 날짜

    Returns:
        tuple: (total_return, cagr, max_drawdown, volatility, sharpe_ratio)
    """
    # 총 수익률
    total_return = final_val - 100

    # 연환산 수익률 (CAGR)
    years = (end_date - start_date).days / 365.25
    cagr = ((final_val / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

    # 최대 낙폭 (MDD)
    cum_ret = (1 + daily_ret_series).cumprod()
    max_drawdown = (cum_ret / cum_ret.cummax() - 1.0).min() * 100

    # 변동성 (연환산)
    volatility = daily_ret_series.std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100

    # 샤프 비율
    sharpe = (cagr - RISK_FREE_RATE) / volatility if volatility > 0 else 0

    return total_return, cagr, max_drawdown, volatility, sharpe
