"""백테스트 계산 모듈"""

import numpy as np
import pandas as pd

from config import (
    FX_TICKERS,
    KRW_ASSET_SUFFIXES,
    KRW_ASSET_TICKERS
)


def _apply_fx_conversion(df_calc, portfolio, benchmark_ticker):
    """환율 변환 적용"""
    usd_krw = df_calc.get(FX_TICKERS["USD_KRW"])
    jpy_krw = df_calc.get(FX_TICKERS["JPY_KRW"])

    # 포트폴리오 자산에 환율 적용
    for asset in portfolio:
        ticker = asset['ticker']
        currency = asset.get('currency', 'USD')

        if ticker in df_calc.columns:
            if currency == 'USD' and usd_krw is not None:
                df_calc[ticker] = df_calc[ticker] * usd_krw
            elif currency == 'JPY' and jpy_krw is not None:
                df_calc[ticker] = df_calc[ticker] * jpy_krw

    # 벤치마크에 환율 적용
    if benchmark_ticker in df_calc.columns:
        is_krw_asset = (
            benchmark_ticker.endswith(KRW_ASSET_SUFFIXES) or
            benchmark_ticker in KRW_ASSET_TICKERS
        )

        if not is_krw_asset:
            if benchmark_ticker.endswith('.T') and jpy_krw is not None:
                df_calc[benchmark_ticker] = df_calc[benchmark_ticker] * jpy_krw
            elif usd_krw is not None:
                df_calc[benchmark_ticker] = df_calc[benchmark_ticker] * usd_krw

    return df_calc


def _get_rebalance_months(rebalance_type, start_month):
    """리밸런싱 대상 월 계산"""
    if rebalance_type == 'Yearly':
        return [start_month]
    elif rebalance_type == 'Semi-Annually':
        return [start_month, (start_month + 6 - 1) % 12 + 1]
    elif rebalance_type == 'Quarterly':
        return [((start_month + i * 3 - 1) % 12 + 1) for i in range(4)]
    elif rebalance_type == 'Monthly':
        return list(range(1, 13))
    return []


def calculate_portfolio(data, portfolio, benchmark_ticker, rebalance_type, rebalance_month, apply_fx=False):
    """
    포트폴리오 백테스트 계산

    Args:
        data: 가격 데이터 DataFrame
        portfolio: 포트폴리오 리스트 [{'ticker': str, 'weight': float, ...}, ...]
        benchmark_ticker: 벤치마크 티커
        rebalance_type: 리밸런싱 유형 (None, Yearly, Semi-Annually, Quarterly, Monthly)
        rebalance_month: 리밸런싱 시작 월
        apply_fx: KRW 환산 여부

    Returns:
        DataFrame: 백테스트 결과
    """
    df_calc = data.copy()

    # 환율 변환 적용
    if apply_fx:
        df_calc = _apply_fx_conversion(df_calc, portfolio, benchmark_ticker)

    # 일별 수익률 계산
    daily_returns = df_calc.pct_change().dropna()
    if daily_returns.empty:
        return pd.DataFrame()

    # 포트폴리오 티커 및 비중 설정
    port_tickers = [asset['ticker'] for asset in portfolio]
    if benchmark_ticker not in daily_returns.columns:
        return pd.DataFrame()

    weights_map = {asset['ticker']: asset['weight'] for asset in portfolio}
    valid_tickers = [t for t in port_tickers if t in daily_returns.columns]
    valid_weights = [weights_map.get(t, 0.0) for t in valid_tickers]

    if sum(valid_weights) == 0:
        return pd.DataFrame()

    # 비중 정규화
    current_weights = np.array(valid_weights) / sum(valid_weights)
    target_weights = current_weights.copy()

    # 리밸런싱 월 계산
    target_months = _get_rebalance_months(rebalance_type, rebalance_month)

    # 포트폴리오 수익률 계산
    portfolio_rets = []
    prev_month = daily_returns.index[0].month
    port_returns_df = daily_returns[valid_tickers]

    for date, row in port_returns_df.iterrows():
        curr_month = date.month

        # 월 변경 시 리밸런싱 체크
        if curr_month != prev_month:
            if rebalance_type != 'None' and curr_month in target_months:
                current_weights = target_weights.copy()
            prev_month = curr_month

        # 일별 수익률 계산
        daily_ret = np.dot(row.values, current_weights)
        portfolio_rets.append(daily_ret)

        # 비중 조정 (드리프트)
        current_weights = current_weights * (1 + row.values) / (1 + daily_ret)

    # 결과 DataFrame 생성
    result = pd.DataFrame({'Daily_Ret': portfolio_rets}, index=port_returns_df.index)
    result['Portfolio'] = 100 * (1 + result['Daily_Ret']).cumprod()

    # 벤치마크 추가
    bm_rets = daily_returns[benchmark_ticker]
    result['Benchmark'] = 100 * (1 + bm_rets).cumprod()
    result['BM_Daily_Ret'] = bm_rets

    # 개별 자산 가치 추가
    individual_values = (1 + port_returns_df).cumprod() * 100
    result = pd.concat([result, individual_values], axis=1)

    return result
