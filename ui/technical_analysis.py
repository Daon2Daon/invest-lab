"""Technical Analysis UI 모듈"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

from core.data_fetcher import search_ticker, fetch_ohlcv_data
from core.indicators import (
    calculate_ema,
    calculate_bollinger_bands,
    calculate_rsi,
    calculate_macd,
    calculate_vwap
)
from config import TA_TIMEFRAME_MAP, TA_PERIOD_MAP, TA_EMA_COLORS
from ui.stock_search import add_to_recent_searches
from db.models import get_stock_note, save_stock_note, delete_stock_note
from auth.session import get_current_user


def render_technical_analysis():
    """Technical Analysis 메인 렌더링 함수"""
    # 헤더
    st.markdown(
        '<h1 style="font-size: 28px; font-weight: 700; margin-bottom: 10px;">Technical Analysis</h1>',
        unsafe_allow_html=True
    )
    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    # 다이얼로그에서 종목이 선택되었는지 확인 (다이얼로그 밖에서 처리)
    if st.session_state.get('ta_selected_stock'):
        selected = st.session_state.ta_selected_stock
        # 먼저 삭제 (무한 루프 방지)
        del st.session_state.ta_selected_stock
        # 차트 로드 (내부에서 st.rerun() 호출)
        _load_chart_from_dialog(selected['ticker'], selected['name'], selected['currency'])

    # 입력 컨트롤
    _render_input_controls()

    # 차트 영역
    if st.session_state.get('ta_data') is not None:
        st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
        _render_charts()


@st.dialog("Search Stock", width="large")
def _search_stock_dialog():
    """종목 검색 팝업 다이얼로그"""
    from ui.stock_search import search_stocks, init_search_session, get_user_watchlist
    from auth.session import get_current_user

    init_search_session()
    user = get_current_user()

    # 검색창 (form으로 감싸서 엔터키 지원)
    with st.form(key="ta_search_form", clear_on_submit=False):
        col_search, col_btn = st.columns([3, 1])
        with col_search:
            search_query = st.text_input(
                "Search",
                placeholder="Search by ticker or name (e.g. AAPL, 삼성전자)",
                label_visibility="collapsed",
                key="ta_dialog_search_input"
            )
        with col_btn:
            search_clicked = st.form_submit_button("Search", use_container_width=True)

    # 검색 실행
    if search_clicked and search_query:
        with st.spinner("🔍 Searching..."):
            results = search_stocks(search_query)
            if results:
                st.session_state.ta_dialog_search_results = results
            else:
                st.warning("No results found.")
                st.session_state.ta_dialog_search_results = []

    # 검색 결과 표시
    if st.session_state.get('ta_dialog_search_results'):
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        st.markdown("**Search Results**")
        for i, stock in enumerate(st.session_state.ta_dialog_search_results):
            col_info, col_select = st.columns([3, 1])
            with col_info:
                st.markdown(
                    f"<div style='padding:8px 0;'>"
                    f"<span style='font-weight:600;'>{stock['ticker']}</span> "
                    f"<span style='color:#64748B; font-size:13px;'>{stock['name']}</span> "
                    f"<span style='color:#94A3B8; font-size:12px;'>({stock['currency']})</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with col_select:
                if st.button("Select", key=f"ta_dialog_select_{i}", use_container_width=True):
                    # 선택된 종목 정보만 저장 (다이얼로그에서는 선택만)
                    st.session_state.ta_selected_stock = {
                        'ticker': stock['ticker'],
                        'name': stock['name'],
                        'currency': stock['currency']
                    }
                    st.session_state.ta_dialog_search_results = []
                    st.rerun()

    st.markdown('<div style="height:15px;"></div>', unsafe_allow_html=True)

    # 최근 검색 & Watchlist
    col_recent, col_watchlist = st.columns(2)

    with col_recent:
        recent = st.session_state.get('recent_searches', [])
        if recent:
            st.markdown("**Recent**")
            cols = st.columns(min(len(recent), 5))
            for i, stock in enumerate(recent[:5]):
                with cols[i]:
                    if st.button(stock['ticker'], key=f"ta_dialog_recent_{i}", use_container_width=True):
                        # 선택된 종목 정보만 저장
                        st.session_state.ta_selected_stock = {
                            'ticker': stock['ticker'],
                            'name': stock['name'],
                            'currency': stock['currency']
                        }
                        st.session_state.ta_dialog_search_results = []
                        st.rerun()

    with col_watchlist:
        if user:
            from db.models import get_user_watchlist
            watchlist = get_user_watchlist(user['user_id'])
            if watchlist:
                st.markdown("**Watchlist**")
                display_list = watchlist[:5]
                cols = st.columns(min(len(display_list), 5))
                for i, stock in enumerate(display_list):
                    with cols[i]:
                        if st.button(stock['ticker'], key=f"ta_dialog_watchlist_{i}", use_container_width=True):
                            # 선택된 종목 정보만 저장
                            st.session_state.ta_selected_stock = {
                                'ticker': stock['ticker'],
                                'name': stock['name'],
                                'currency': stock['currency']
                            }
                            st.session_state.ta_dialog_search_results = []
                            st.rerun()


def _load_chart_from_dialog(ticker: str, name: str, currency: str):
    """다이얼로그에서 종목 선택 시 차트 자동 로드"""
    # 먼저 다이얼로그 닫기 (검색 결과 초기화)
    st.session_state.ta_dialog_search_results = []

    # 데이터 로드
    with st.spinner(f"Loading {ticker} chart..."):
        df = fetch_ohlcv_data(ticker=ticker, period='1y', interval='1d')

    # spinner 밖에서 세션 상태 업데이트 (이중 표시 방지)
    if df is not None and not df.empty:
        st.session_state.ta_selected_ticker = ticker
        st.session_state.ta_selected_name = name
        st.session_state.ta_selected_currency = currency
        st.session_state.ta_data = df
        st.session_state.ta_ticker = ticker
        st.session_state.ta_name = name
        st.session_state.ta_currency = currency
        st.session_state.ta_period = '1y'
        st.session_state.ta_interval = '1d'
        # Indicators 초기화
        st.session_state.ta_show_bb = False
        st.session_state.ta_show_rsi = False
        st.session_state.ta_show_macd = False
        st.session_state.ta_show_vwap = False
        # 최근 검색에 추가
        add_to_recent_searches(ticker, name, currency)
        st.rerun()
    else:
        st.error(f"Failed to load chart for {ticker}")


def _render_input_controls():
    """입력 컨트롤 영역 렌더링"""
    # 차트가 로드된 경우: 검색버튼 + 종목정보 표시
    if st.session_state.get('ta_data') is not None:
        ticker = st.session_state.get('ta_ticker', '')
        name = st.session_state.get('ta_name', '')
        currency = st.session_state.get('ta_currency', 'USD')

        col_search, col_info = st.columns([0.18, 0.82])

        with col_search:
            if st.button("🔍", use_container_width=True, help="Search Stock"):
                _search_stock_dialog()

        with col_info:
            # 반응형 폰트 크기 (최소/최대값 제한으로 모바일과 데스크탑 모두 최적화)
            st.markdown(
                f"<div class='asset-row' style='padding: 8px 0; display: flex; align-items: center; flex-wrap: wrap; gap: 8px;'>"
                f"<span class='asset-ticker' style='font-size: clamp(16px, 3.5vw, 20px); font-weight: 700; white-space: nowrap;'>{ticker}</span>"
                f"<span class='asset-name' style='font-size: clamp(13px, 2.5vw, 15px); color: #64748B;'>{name}</span>"
                f"<span class='tag-curr' style='font-size: clamp(11px, 2vw, 13px); background: #F1F5F9; padding: 2px 8px; border-radius: 4px;'>{currency}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        # 차트가 로드되지 않은 경우: 검색버튼만
        if st.button("🔍 Search Stock", use_container_width=True):
            _search_stock_dialog()
        st.caption("Search and select a stock to view the chart.")


def _load_chart_data_direct(ticker: str, timeframe: str, period: str):
    """이미 검증된 티커로 차트 데이터 로드"""
    name = st.session_state.get('ta_selected_name', '')
    currency = st.session_state.get('ta_selected_currency', 'USD')

    # yfinance 파라미터로 변환
    interval = TA_TIMEFRAME_MAP[timeframe]

    with st.spinner(f"Loading {ticker} data..."):
        df = fetch_ohlcv_data(
            ticker=ticker,
            period=period,
            interval=interval
        )

        if df is None or df.empty:
            st.error("Failed to fetch data. Please try again.")
            return

        # 세션에 저장
        st.session_state.ta_data = df
        st.session_state.ta_ticker = ticker
        st.session_state.ta_name = name
        st.session_state.ta_currency = currency
        st.session_state.ta_period = period
        st.session_state.ta_interval = interval
        # Indicators 체크박스 초기화
        st.session_state.ta_show_bb = False
        st.session_state.ta_show_rsi = False
        st.session_state.ta_show_macd = False
        st.session_state.ta_show_vwap = False
        # 최근 검색에 추가
        add_to_recent_searches(ticker, name, currency)
        st.rerun()


def _reload_chart_data(period: str):
    """기간 변경 시 차트 데이터 재로드"""
    ticker = st.session_state.ta_ticker
    interval = st.session_state.get('ta_interval', '1d')

    # Indicator 상태 보존
    indicator_states = {
        'ta_show_bb': st.session_state.get('ta_show_bb', False),
        'ta_show_rsi': st.session_state.get('ta_show_rsi', False),
        'ta_show_macd': st.session_state.get('ta_show_macd', False),
        'ta_show_vwap': st.session_state.get('ta_show_vwap', False),
    }

    with st.spinner(f"Loading {ticker} data..."):
        df = fetch_ohlcv_data(
            ticker=ticker,
            period=period,
            interval=interval
        )

        if df is None or df.empty:
            st.error("Failed to fetch data. Please try again.")
            return

        # 세션에 저장
        st.session_state.ta_data = df
        st.session_state.ta_period = period

        # Indicator 상태 복원
        for key, value in indicator_states.items():
            st.session_state[key] = value

        st.rerun()


def _reload_chart_with_interval(interval: str):
    """Timeframe 변경 시 차트 데이터 재로드"""
    ticker = st.session_state.ta_ticker
    period = st.session_state.get('ta_period', '1y')

    # Indicator 상태 보존
    indicator_states = {
        'ta_show_bb': st.session_state.get('ta_show_bb', False),
        'ta_show_rsi': st.session_state.get('ta_show_rsi', False),
        'ta_show_macd': st.session_state.get('ta_show_macd', False),
        'ta_show_vwap': st.session_state.get('ta_show_vwap', False),
    }

    with st.spinner(f"Loading {ticker} data..."):
        df = fetch_ohlcv_data(
            ticker=ticker,
            period=period,
            interval=interval
        )

        if df is None or df.empty:
            st.error("Failed to fetch data. Please try again.")
            return

        # 세션에 저장
        st.session_state.ta_data = df
        st.session_state.ta_interval = interval

        # Indicator 상태 복원
        for key, value in indicator_states.items():
            st.session_state[key] = value

        st.rerun()


def _render_charts():
    """차트 렌더링"""
    df = st.session_state.ta_data
    ticker = st.session_state.ta_ticker
    name = st.session_state.ta_name
    currency = st.session_state.ta_currency

    # 1행: Timeframe & Data Period (좌우 배치)
    col_tf, col_period = st.columns(2)

    with col_tf:
        st.markdown('<div class="section-label">Timeframe</div>', unsafe_allow_html=True)
        current_interval = st.session_state.get('ta_interval', '1d')
        current_tf_label = next((k for k, v in TA_TIMEFRAME_MAP.items() if v == current_interval), "Daily")
        timeframe = st.selectbox(
            "Timeframe",
            options=list(TA_TIMEFRAME_MAP.keys()),
            index=list(TA_TIMEFRAME_MAP.keys()).index(current_tf_label),
            label_visibility="collapsed",
            key="ta_timeframe_chart"
        )
        new_interval = TA_TIMEFRAME_MAP[timeframe]
        if new_interval != current_interval:
            _reload_chart_with_interval(new_interval)

    with col_period:
        st.markdown('<div class="section-label">Data Period</div>', unsafe_allow_html=True)
        period_options = {
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y",
            "Max": "max"
        }
        current_period = st.session_state.get('ta_period', '1y')
        current_label = next((k for k, v in period_options.items() if v == current_period), "1 Year")
        selected_label = st.selectbox(
            "Period",
            options=list(period_options.keys()),
            index=list(period_options.keys()).index(current_label),
            label_visibility="collapsed",
            key="ta_period_select"
        )
        selected_period = period_options[selected_label]
        if selected_period != current_period:
            _reload_chart_data(selected_period)

    # 2행: Indicators (한 줄 배치 + 전체 선택/해제)
    st.markdown('<div class="section-label">Indicators</div>', unsafe_allow_html=True)

    col_all, col_bb, col_rsi, col_macd, col_vwap = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])

    with col_all:
        # 현재 모든 indicator 상태 확인
        all_selected = all([
            st.session_state.get('ta_show_bb', False),
            st.session_state.get('ta_show_rsi', False),
            st.session_state.get('ta_show_macd', False),
            st.session_state.get('ta_show_vwap', False)
        ])
        if st.button("All" if not all_selected else "None", use_container_width=True, type="secondary"):
            new_state = not all_selected
            st.session_state.ta_show_bb = new_state
            st.session_state.ta_show_rsi = new_state
            st.session_state.ta_show_macd = new_state
            st.session_state.ta_show_vwap = new_state
            st.rerun()

    with col_bb:
        st.checkbox("BB", key="ta_show_bb", help="Bollinger Bands")
    with col_rsi:
        st.checkbox("RSI", key="ta_show_rsi")
    with col_macd:
        st.checkbox("MACD", key="ta_show_macd")
    with col_vwap:
        st.checkbox("VWAP", key="ta_show_vwap")

    # 선택된 indicators 리스트 생성 (세션 상태에서 직접 읽기)
    indicators = []
    if st.session_state.get('ta_show_bb', False):
        indicators.append("Bollinger Bands")
    if st.session_state.get('ta_show_rsi', False):
        indicators.append("RSI")
    if st.session_state.get('ta_show_macd', False):
        indicators.append("MACD")
    if st.session_state.get('ta_show_vwap', False):
        indicators.append("VWAP")

    st.markdown('<div style="height:15px;"></div>', unsafe_allow_html=True)

    # 서브플롯 개수 및 높이 결정
    num_subplots = 2  # 캔들스틱 + 거래량 (기본)
    if "RSI" in indicators:
        num_subplots += 1
    if "MACD" in indicators:
        num_subplots += 1

    # 높이 비율 설정
    if num_subplots == 2:
        row_heights = [0.75, 0.25]
    elif num_subplots == 3:
        row_heights = [0.6, 0.2, 0.2]
    else:
        row_heights = [0.5, 0.17, 0.17, 0.16]

    fig = make_subplots(
        rows=num_subplots,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights
    )

    # 1. 캔들스틱 차트
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price",
            increasing_line_color='#10B981',
            decreasing_line_color='#EF4444'
        ),
        row=1, col=1
    )

    # 2. EMA (항상 표시)
    ema_data = calculate_ema(df['Close'])
    for period, ema in ema_data.items():
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=ema,
                name=f"EMA {period}",
                line=dict(width=1.5, color=TA_EMA_COLORS.get(period, '#888888'))
            ),
            row=1, col=1
        )

    # 3. 볼린저 밴드 (선택적)
    if "Bollinger Bands" in indicators:
        bb = calculate_bollinger_bands(df['Close'])
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=bb['upper'],
                name='BB Upper',
                line=dict(width=1, color='#94A3B8', dash='dash')
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=bb['lower'],
                name='BB Lower',
                line=dict(width=1, color='#94A3B8', dash='dash'),
                fill='tonexty',
                fillcolor='rgba(148,163,184,0.1)'
            ),
            row=1, col=1
        )

    # 4. VWAP (선택적)
    if "VWAP" in indicators:
        vwap = calculate_vwap(df)
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=vwap,
                name='VWAP',
                line=dict(width=2, color='#EC4899', dash='dot')
            ),
            row=1, col=1
        )

    # 5. 거래량 바 차트
    colors = ['#10B981' if c >= o else '#EF4444'
              for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    # 6. RSI 서브플롯 (선택적)
    current_row = 3
    if "RSI" in indicators:
        rsi = calculate_rsi(df['Close'])
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=rsi,
                name='RSI',
                line=dict(width=1.5, color='#8B5CF6')
            ),
            row=current_row, col=1
        )
        # 과매수/과매도 라인
        fig.add_hline(y=70, line_dash="dash", line_color="#EF4444",
                      line_width=1, row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#10B981",
                      line_width=1, row=current_row, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1)
        current_row += 1

    # 7. MACD 서브플롯 (선택적)
    if "MACD" in indicators:
        macd = calculate_macd(df['Close'])
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=macd['macd'],
                name='MACD',
                line=dict(width=1.5, color='#3B82F6')
            ),
            row=current_row, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=macd['signal'],
                name='Signal',
                line=dict(width=1.5, color='#F59E0B')
            ),
            row=current_row, col=1
        )
        # 히스토그램
        hist_colors = ['#10B981' if v >= 0 else '#EF4444' for v in macd['histogram']]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=macd['histogram'],
                name='Histogram',
                marker_color=hist_colors,
                opacity=0.7
            ),
            row=current_row, col=1
        )
        fig.update_yaxes(title_text="MACD", row=current_row, col=1)

    # 레이아웃 설정
    chart_height = 500 + (num_subplots - 2) * 120
    fig.update_layout(
        template='plotly_white',
        height=chart_height,
        margin=dict(t=20, b=20, l=60, r=20),
        xaxis_rangeslider_visible=False,
        dragmode=False,  # 드래그로 차트 이동 비활성화 (모바일 스크롤 개선)
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        hovermode="x unified"
    )

    # x축 날짜 형식 설정
    fig.update_xaxes(type="date", row=1, col=1)

    # 파일명 생성: {ticker}_{timeframe}_{YYYYMMDD}.png
    current_interval = st.session_state.get('ta_interval', '1d')
    timeframe_label = next((k for k, v in TA_TIMEFRAME_MAP.items() if v == current_interval), "Daily")
    today = datetime.now().strftime("%Y%m%d")
    filename = f"{ticker}_{timeframe_label}_{today}"

    # Plotly config - 모바일 친화적 설정
    config = {
        'scrollZoom': False,  # 스크롤로 줌 비활성화 (모바일 스크롤 가능)
        'displayModeBar': 'hover',  # 툴바는 호버/터치 시에만 표시
        'doubleClick': 'reset',  # 더블클릭 시 차트 리셋
        'modeBarButtonsToRemove': [
            'pan2d',  # 패닝 도구 제거
            'lasso2d',  # 올가미 선택 제거
            'select2d'  # 박스 선택 제거
        ],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': filename,
            'height': chart_height,
            'width': 1400,
            'scale': 2
        }
    }

    st.plotly_chart(fig, use_container_width=True, config=config)

    # 메모 섹션 추가
    _render_notes_section(ticker, name)


def _render_notes_section(ticker: str, name: str):
    """메모 섹션 렌더링"""
    user = get_current_user()
    if not user:
        return

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Stock Notes</div>', unsafe_allow_html=True)

    # 현재 종목의 메모 로드
    existing_note = get_stock_note(user['user_id'], ticker)
    note_content = existing_note['note_content'] if existing_note else ""

    # 세션 상태 초기화 (종목 변경 시 메모 업데이트)
    session_key = f"note_{ticker}"
    if session_key not in st.session_state:
        st.session_state[session_key] = note_content

    with st.container(border=True):
        # 메모 입력 영역
        note_text = st.text_area(
            "Note",
            value=st.session_state[session_key],
            height=300,
            placeholder=f"{ticker} ({name})에 대한 분석 메모를 작성하세요...",
            label_visibility="collapsed",
            key=f"note_input_{ticker}"
        )

        # 버튼 및 정보 영역
        col_btn1, col_btn2, col_info = st.columns([0.15, 0.15, 0.7])

        with col_btn1:
            if st.button("Save", use_container_width=True, type="primary"):
                save_stock_note(user['user_id'], ticker, name, note_text)
                st.session_state[session_key] = note_text
                st.success("메모가 저장되었습니다!")
                st.rerun()

        with col_btn2:
            if st.button("Delete", use_container_width=True, disabled=not existing_note):
                if delete_stock_note(user['user_id'], ticker):
                    st.session_state[session_key] = ""
                    st.success("메모가 삭제되었습니다!")
                    st.rerun()

        with col_info:
            if existing_note:
                updated_at = existing_note.get('updated_at', '')
                if updated_at:
                    # YYYY-MM-DD HH:MM:SS 형식에서 날짜와 시간만 표시
                    try:
                        dt_str = updated_at[:16].replace('T', ' ')  # 2026-01-02T15:30:00 -> 2026-01-02 15:30
                        st.markdown(
                            f"<div style='text-align:right; color:#94A3B8; font-size:13px; padding-top:8px;'>"
                            f"Last updated: {dt_str}</div>",
                            unsafe_allow_html=True
                        )
                    except:
                        pass
