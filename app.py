"""Invest Lab - 메인 애플리케이션"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

# 모듈 imports
from dotenv import load_dotenv
from db.database import init_database
from auth.session import (
    init_session_state, is_authenticated, get_current_user,
    logout_user, is_admin, reset_backtest_state
)
from auth.authentication import change_password
from ui.login_page import render_login_page
from ui.admin_panel import render_admin_panel
from ui.technical_analysis import render_technical_analysis
from ui.stock_search import render_stock_search, add_to_recent_searches
from ui.styles import apply_styles
from db.models import get_user_portfolios, save_portfolio, delete_portfolio, get_user_stock_notes, delete_stock_note
from core.data_fetcher import search_ticker, fetch_data_robust, fetch_ohlcv_data
from core.backtest import calculate_portfolio
from core.metrics import calculate_metrics
from core.analysis import generate_ai_analysis
from config import (
    BENCHMARK_MAP, ASSET_TYPES, REBALANCE_OPTIONS,
    DEFAULT_START_YEAR, WEIGHT_TOLERANCE, GEMINI_API_KEY
)

# 환경변수 및 DB 초기화
load_dotenv()
init_database()

# ---------------------------------------------------------
# 페이지 설정 및 스타일
# ---------------------------------------------------------
st.set_page_config(page_title="Invest Lab", layout="wide")
apply_styles(st)

# 세션 상태 초기화
init_session_state()

# 인증 확인
if not is_authenticated():
    render_login_page()
    st.stop()

current_user = get_current_user()


# ---------------------------------------------------------
# 헬퍼 함수
# ---------------------------------------------------------
@st.dialog("Change Password", width="large")
def change_password_dialog():
    """비밀번호 변경 다이얼로그"""
    st.markdown("### Change Your Password")
    st.markdown("Please enter your current password and new password.")
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

    # 입력 필드
    current_password = st.text_input(
        "Current Password",
        type="password",
        key="change_pwd_current"
    )

    new_password = st.text_input(
        "New Password",
        type="password",
        key="change_pwd_new"
    )

    confirm_password = st.text_input(
        "Confirm New Password",
        type="password",
        key="change_pwd_confirm"
    )

    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

    # 변경 버튼
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Change Password", type="primary", use_container_width=True):
            # 입력 검증
            if not current_password or not new_password or not confirm_password:
                st.error("모든 필드를 입력해주세요.")
                return

            if new_password != confirm_password:
                st.error("새 비밀번호가 일치하지 않습니다.")
                return

            # 비밀번호 변경
            user = get_current_user()
            success, message = change_password(user['user_id'], current_password, new_password)

            if success:
                st.success(message)
                # 2초 후 다이얼로그 닫기
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error(message)

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


def load_saved_portfolios():
    """현재 사용자의 포트폴리오를 DB에서 로드"""
    user = get_current_user()
    portfolios = get_user_portfolios(user['user_id'])
    return {p['portfolio_name']: json.loads(p['portfolio_data']) for p in portfolios}


def save_portfolio_to_file(name, portfolio_data):
    """현재 사용자의 포트폴리오를 DB에 저장"""
    user = get_current_user()
    save_portfolio(user['user_id'], name, json.dumps(portfolio_data))


def delete_portfolio_from_file(name):
    """현재 사용자의 포트폴리오를 DB에서 삭제"""
    user = get_current_user()
    delete_portfolio(user['user_id'], name)


def plot_allocation(portfolio):
    """자산 배분 차트 생성"""
    if not portfolio:
        return None, None

    df_alloc = pd.DataFrame(portfolio)

    # 컬럼 기본값 설정
    if 'type' not in df_alloc.columns:
        df_alloc['type'] = 'Stock'
    else:
        df_alloc['type'] = df_alloc['type'].fillna('Stock')

    if 'currency' not in df_alloc.columns:
        df_alloc['currency'] = 'USD'
    else:
        df_alloc['currency'] = df_alloc['currency'].fillna('USD')

    df_alloc = df_alloc[df_alloc['weight'] > 0]
    if df_alloc.empty:
        return None, None

    colors = px.colors.qualitative.Set2

    # 자산 유형 차트
    fig_type = px.pie(
        df_alloc, values='weight', names='type', hole=0.5,
        color_discrete_sequence=colors, title="By Asset Type"
    )
    fig_type.update_traces(textinfo='percent', textposition='inside')
    fig_type.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        margin=dict(t=40, b=20, l=10, r=10), height=280
    )

    # 통화 차트
    fig_curr = px.pie(
        df_alloc, values='weight', names='currency', hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Pastel, title="By Currency"
    )
    fig_curr.update_traces(textinfo='percent', textposition='inside')
    fig_curr.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        margin=dict(t=40, b=20, l=10, r=10), height=280
    )

    return fig_type, fig_curr


# ---------------------------------------------------------
# 사이드바 UI
# ---------------------------------------------------------
with st.sidebar:
    # 사용자 정보 표시
    st.markdown(f"""
        <div style="background: #F8FAFC; padding: 16px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 20px;">
            <div style="font-size: 12px; color: #64748B; margin-bottom: 4px;">Logged in as</div>
            <div style="font-size: 16px; font-weight: 600; color: #0F172A;">{current_user['username']}</div>
        </div>
    """, unsafe_allow_html=True)

    col_pwd, col_logout = st.columns(2)
    with col_pwd:
        if st.button("Password", key="sidebar_change_pwd_btn", use_container_width=True):
            change_password_dialog()
    with col_logout:
        if st.button("Logout", key="sidebar_logout_btn", use_container_width=True):
            logout_user()
            st.rerun()

    st.markdown("---")

    # 메뉴 선택
    st.markdown('<div class="sidebar-section-header">MENU</div>', unsafe_allow_html=True)

    menu_options = ["Portfolio Backtest", "Technical Analysis"]
    if is_admin():
        menu_options.append("Admin Panel")

    current_menu = st.session_state.selected_menu
    if current_menu not in menu_options:
        current_menu = menu_options[0]

    selected_menu = st.radio(
        "Navigation",
        menu_options,
        index=menu_options.index(current_menu),
        label_visibility="collapsed",
        key="menu_radio"
    )

    st.session_state.selected_menu = selected_menu
    st.markdown("---")

    # Portfolio Backtest 메뉴일 때만 Strategy Library 표시
    if st.session_state.selected_menu == "Portfolio Backtest":
        st.markdown('<div class="sidebar-section-header">STRATEGY LIBRARY</div>', unsafe_allow_html=True)

        saved_portfolios = load_saved_portfolios()
        tab_load, tab_save = st.tabs(["Load", "Save"])

        with tab_load:
            if saved_portfolios:
                sel_name = st.selectbox("Select Strategy", list(saved_portfolios.keys()), label_visibility="collapsed")
                c1, c2 = st.columns(2)
                if c1.button("Load", use_container_width=True):
                    st.session_state.portfolio = saved_portfolios[sel_name]
                    reset_backtest_state()
                    st.rerun()
                if c2.button("Del", use_container_width=True):
                    delete_portfolio_from_file(sel_name)
                    st.rerun()
            else:
                st.caption("No saved strategies.")

        with tab_save:
            save_name = st.text_input("Name", placeholder="New Strategy Name", label_visibility="collapsed")
            if st.button("Save", use_container_width=True):
                if not st.session_state.portfolio:
                    st.warning("Empty portfolio.")
                elif save_name:
                    save_portfolio_to_file(save_name, st.session_state.portfolio)
                    st.success("Saved.")

    # Technical Analysis 메뉴일 때만 My Notes 표시
    if st.session_state.selected_menu == "Technical Analysis":
        st.markdown('<div class="sidebar-section-header">MY NOTES</div>', unsafe_allow_html=True)

        user_notes = get_user_stock_notes(current_user['user_id'])

        if user_notes:
            # 선택 옵션 생성: ticker (name)
            note_options = {
                f"{n['ticker']} ({n['name'][:10]}...)" if n.get('name') and len(n.get('name', '')) > 10
                else f"{n['ticker']} ({n.get('name', '')})" if n.get('name')
                else n['ticker']: n
                for n in user_notes
            }

            selected_label = st.selectbox(
                "Select Note",
                list(note_options.keys()),
                label_visibility="collapsed"
            )
            selected_note = note_options[selected_label]

            # Load / Del 버튼
            c1, c2 = st.columns(2)
            if c1.button("Load", key="load_selected_note", use_container_width=True):
                ticker = selected_note['ticker']
                name = selected_note.get('name', '')

                # 티커에서 currency 추론
                if ticker.endswith('.KS') or ticker.endswith('.KQ'):
                    currency = 'KRW'
                elif ticker.endswith('.T'):
                    currency = 'JPY'
                else:
                    currency = 'USD'

                # 차트 데이터 자동 로드
                df = fetch_ohlcv_data(ticker=ticker, period='1y', interval='1d')

                if df is not None and not df.empty:
                    # 세션 상태 업데이트
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
                else:
                    st.error(f"Failed to load chart for {ticker}")
                st.rerun()

            if c2.button("Del", key="del_selected_note", use_container_width=True):
                delete_stock_note(current_user['user_id'], selected_note['ticker'])
                st.rerun()
        else:
            st.caption("No notes yet.")
            st.caption("Add notes in Technical Analysis.")


# ---------------------------------------------------------
# 종목 검색 다이얼로그
# ---------------------------------------------------------
@st.dialog("Search Stock", width="large")
def search_stock_dialog():
    """종목 검색 팝업 다이얼로그"""
    from ui.stock_search import search_stocks, add_to_recent_searches, init_search_session, get_user_watchlist
    from db.models import is_in_watchlist, add_to_watchlist, remove_from_watchlist

    init_search_session()
    user = get_current_user()

    # 검색창 (form으로 감싸서 엔터키 지원)
    with st.form(key="pf_search_form", clear_on_submit=False):
        col_search, col_btn = st.columns([3, 1])
        with col_search:
            search_query = st.text_input(
                "Search",
                placeholder="Search by ticker or name (e.g. AAPL, 삼성전자, cswind)",
                label_visibility="collapsed",
                key="dialog_search_input"
            )
        with col_btn:
            search_clicked = st.form_submit_button("Search", use_container_width=True)

    # 검색 실행
    if search_clicked and search_query:
        with st.spinner("🔍 Searching..."):
            results = search_stocks(search_query)
            if results:
                st.session_state.dialog_search_results = results
            else:
                st.warning("No results found.")
                st.session_state.dialog_search_results = []

    # 검색 결과 표시
    if st.session_state.get('dialog_search_results'):
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        st.markdown("**Search Results**")
        for i, stock in enumerate(st.session_state.dialog_search_results):
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
                if st.button("Select", key=f"dialog_select_{i}", use_container_width=True):
                    st.session_state.pf_selected_ticker = stock['ticker']
                    st.session_state.pf_selected_name = stock['name']
                    st.session_state.pf_selected_currency = stock['currency']
                    st.session_state.dialog_search_results = []
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
                    if st.button(stock['ticker'], key=f"dialog_recent_{i}", use_container_width=True):
                        st.session_state.pf_selected_ticker = stock['ticker']
                        st.session_state.pf_selected_name = stock['name']
                        st.session_state.pf_selected_currency = stock['currency']
                        st.rerun()

    with col_watchlist:
        if user:
            from db.models import get_user_watchlist
            watchlist = get_user_watchlist(user['user_id'])
            if watchlist:
                st.markdown("**★ Watchlist**")
                display_list = watchlist[:5]
                cols = st.columns(min(len(display_list), 5))
                for i, stock in enumerate(display_list):
                    with cols[i]:
                        if st.button(stock['ticker'], key=f"dialog_watchlist_{i}", use_container_width=True):
                            st.session_state.pf_selected_ticker = stock['ticker']
                            st.session_state.pf_selected_name = stock['name']
                            st.session_state.pf_selected_currency = stock['currency']
                            st.rerun()


# ---------------------------------------------------------
# 메인 화면: Portfolio Backtest
# ---------------------------------------------------------
if st.session_state.selected_menu == "Portfolio Backtest":
    st.markdown("<h1 style=\"font-size: 28px; font-weight: 700; margin-bottom: 10px;\">Portfolio Backtest</h1>", unsafe_allow_html=True)
    st.markdown("<div style=\"height:20px;\"></div>", unsafe_allow_html=True)

    # --- 1. 자산 추가 ---
    st.markdown('<div class="section-label">Add Asset</div>', unsafe_allow_html=True)

    # 검색 버튼 - 다이얼로그 열기
    if st.button("🔍 Search Stock", use_container_width=True):
        search_stock_dialog()

    # 선택된 종목이 있으면 자산 유형 선택 및 추가 버튼 표시
    selected_ticker = st.session_state.get('pf_selected_ticker')
    if selected_ticker:
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        with st.container(border=True):
            name = st.session_state.get('pf_selected_name', '')
            currency = st.session_state.get('pf_selected_currency', 'USD')

            st.markdown(
                f"<div style='margin-bottom:10px;'>"
                f"<span style='font-weight:600;'>{selected_ticker}</span> "
                f"<span style='color:#64748B; font-size:13px;'>{name}</span> "
                f"<span style='color:#94A3B8; font-size:12px;'>({currency})</span>"
                f"</div>",
                unsafe_allow_html=True
            )

            asset_type = st.selectbox("Asset Type", ASSET_TYPES, key="pf_asset_type")

            if st.button("Add to Portfolio", type="primary", use_container_width=True):
                if any(p['ticker'] == selected_ticker for p in st.session_state.portfolio):
                    st.warning("Already added.")
                else:
                    st.session_state.portfolio.append({
                        'ticker': selected_ticker,
                        'name': name,
                        'weight': 0.0,
                        'type': asset_type,
                        'currency': currency
                    })
                    add_to_recent_searches(selected_ticker, name, currency)
                    # 선택 초기화
                    st.session_state.pf_selected_ticker = None
                    st.session_state.pf_selected_name = None
                    st.session_state.pf_selected_currency = None
                    st.rerun()
    else:
        st.caption("Search and select a stock to add.")

    st.markdown("<div style=\"height: 20px\"></div>", unsafe_allow_html=True)

    # --- 2. 포트폴리오 자산 목록 (별도 섹션) ---
    st.markdown(f'<div class="section-label">Portfolio Assets ({len(st.session_state.portfolio)})</div>', unsafe_allow_html=True)

    if not st.session_state.portfolio:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 40px; text-align: center; color: #64748B;">
            <div style="font-weight: 500;">자산이 없습니다.</div>
            <div style="font-size: 13px;">위에서 종목을 검색하여 추가해주세요.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        to_remove = []

        # Asset Type별로 그룹화
        from collections import defaultdict
        grouped_portfolio = defaultdict(list)
        for i, p in enumerate(st.session_state.portfolio):
            asset_type = p.get('type', 'Stock')
            grouped_portfolio[asset_type].append((i, p))

        # 자산 목록 (타입별 그룹화)
        with st.container(border=True):
            group_count = 0
            for asset_type in ASSET_TYPES:  # config.py에 정의된 순서대로 표시
                if asset_type not in grouped_portfolio:
                    continue

                # 그룹 헤더
                if group_count > 0:
                    st.markdown("<hr style='margin:6px 0; border:none; border-top:2px solid #E2E8F0;'>", unsafe_allow_html=True)

                st.markdown(
                    f"<div style='font-weight:600; font-size:12px; color:#475569; margin-bottom:2px;'>"
                    f"{asset_type} ({len(grouped_portfolio[asset_type])})"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # 그룹 내 자산들
                for idx, (i, p) in enumerate(grouped_portfolio[asset_type]):
                    c1, c2, c3, c4, c5 = st.columns([0.30, 0.10, 0.10, 0.40, 0.10])
                    with c1:
                        st.markdown(
                            f"<div class='asset-row'>"
                            f"<span class='asset-ticker'>{p['ticker']}</span>"
                            f"<span class='asset-name'>{p['name'][:15]}{'...' if len(p['name']) > 15 else ''}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    with c2:
                        st.markdown(f"<div class='asset-row'><span class='tag-type'>{p.get('type','Stock')}</span></div>", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"<div class='asset-row'><span class='tag-curr'>{p.get('currency','USD')}</span></div>", unsafe_allow_html=True)
                    with c4:
                        new_w = st.number_input("w", value=float(p['weight']), key=f"w_{i}", step=5.0, label_visibility="collapsed", format="%.2f")
                        st.session_state.portfolio[i]['weight'] = new_w
                    with c5:
                        if st.button("✕", key=f"del_{i}", use_container_width=True):
                            to_remove.append(i)

                    if idx < len(grouped_portfolio[asset_type]) - 1:
                        st.markdown("<hr style='margin:1px 0; border:none; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)

                group_count += 1

        # 삭제 처리
        if to_remove:
            for idx in sorted(set(to_remove), reverse=True):
                del st.session_state.portfolio[idx]
            st.rerun()

        tot_w = sum(p['weight'] for p in st.session_state.portfolio)
        color = '#10B981' if abs(tot_w - 100) <= WEIGHT_TOLERANCE else '#EF4444'
        st.markdown(f"<div style=\"text-align:right; font-weight:700; color:{color}; margin-top:10px;\">Total Weight: {tot_w:.1f}%</div>", unsafe_allow_html=True)

    # 자산 배분 차트
    if st.session_state.portfolio:
        st.markdown("<div style=\"height: 10px\"></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Current Asset & Currency Allocation</div>', unsafe_allow_html=True)
        f_type, f_curr = plot_allocation(st.session_state.portfolio)
        if f_type and f_curr:
            ac1, ac2 = st.columns(2)
            with ac1:
                st.plotly_chart(f_type, use_container_width=True)
            with ac2:
                st.plotly_chart(f_curr, use_container_width=True)

    st.markdown("---")

    # --- 2. 설정 (기간, 벤치마크) ---
    col_row2_1, col_row2_2 = st.columns(2, gap="large")
    with col_row2_1:
        st.markdown('<div class="section-label">Investment Period</div>', unsafe_allow_html=True)
        with st.container(border=True):
            d1, d2 = st.columns(2)
            s_date = d1.date_input("Start", datetime(DEFAULT_START_YEAR, 1, 1), label_visibility="collapsed")
            e_date = d2.date_input("End", datetime.today(), label_visibility="collapsed")
    with col_row2_2:
        st.markdown('<div class="section-label">Benchmark</div>', unsafe_allow_html=True)
        with st.container(border=True):
            bm_label = st.selectbox("Benchmark", list(BENCHMARK_MAP.keys()), index=0, label_visibility="collapsed")
            bm_ticker = BENCHMARK_MAP[bm_label]

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. 리밸런싱 및 옵션 ---
    col_row3_1, col_row3_2 = st.columns(2, gap="large")
    with col_row3_1:
        st.markdown('<div class="section-label">Rebalancing</div>', unsafe_allow_html=True)
        with st.container(border=True):
            rb1, rb2 = st.columns(2)
            rebal_freq = rb1.selectbox("Freq", REBALANCE_OPTIONS, index=0, label_visibility="collapsed")
            disabled_month = rebal_freq in ["None", "Monthly"]
            rebal_month = rb2.selectbox("Month", range(1, 13), index=0, disabled=disabled_month, label_visibility="collapsed", format_func=lambda x: f"{x}월")
    with col_row3_2:
        st.markdown('<div class="section-label">Options</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div style=\"height:4px\"></div>", unsafe_allow_html=True)
            apply_fx = st.checkbox("KRW 환산 (Convert to KRW)", value=False)
            st.markdown("<div style=\"height:4px\"></div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- 4. 실행 버튼 ---
    _, col_btn, _ = st.columns([1, 1.5, 1])
    with col_btn:
        tot_w = sum(p['weight'] for p in st.session_state.portfolio) if st.session_state.portfolio else 0
        is_ready = st.session_state.portfolio and (abs(tot_w - 100) <= WEIGHT_TOLERANCE)
        run_btn = st.button("Run Backtest", type="primary", use_container_width=True, disabled=not is_ready)
        if not is_ready and st.session_state.portfolio:
            st.caption(f"총 비중을 100%로 맞춰주세요. (현재: {tot_w:.0f}%)")

    # --- 결과 렌더링 ---
    if run_btn:
        reset_backtest_state()
        with st.spinner("Calculating..."):
            tickers = [p['ticker'] for p in st.session_state.portfolio]
            data = fetch_data_robust(tickers, bm_ticker, s_date, e_date)
            if data is None or data.empty:
                st.error("데이터를 가져올 수 없습니다. 티커나 기간을 확인해주세요.")
            else:
                res = calculate_portfolio(data, st.session_state.portfolio, bm_ticker, rebal_freq, rebal_month, apply_fx)
                if res.empty:
                    st.error("계산 실패.")
                else:
                    p_metrics = calculate_metrics(res['Daily_Ret'], res['Portfolio'].iloc[-1], s_date, e_date)
                    b_metrics = calculate_metrics(res['BM_Daily_Ret'], res['Benchmark'].iloc[-1], s_date, e_date)
                    st.session_state.sim_result = {
                        'df': res, 'p_metrics': p_metrics, 'b_metrics': b_metrics, 'bm_label': bm_label
                    }
                    st.rerun()

    if st.session_state.sim_result:
        data = st.session_state.sim_result
        df = data['df']
        pm = data['p_metrics']
        bm = data['b_metrics']
        bm_name = data['bm_label']

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Simulation Results</div>', unsafe_allow_html=True)

        # 결과 요약 카드
        with st.container(border=True):
            col_m = st.columns(5)
            labels = ["Total Return", "CAGR", "Max Drawdown", "Volatility", "Sharpe Ratio"]
            formats = ["{:.2f}%", "{:.2f}%", "{:.2f}%", "{:.2f}%", "{:.2f}"]
            for i, col in enumerate(col_m):
                val = pm[i]
                bm_val = bm[i]
                diff = val - bm_val
                delta_color = "inverse" if i in [2, 3] else "normal"
                col.metric(labels[i], formats[i].format(val), f"{diff:.2f} vs BM" if i != 4 else f"{diff:.2f}", delta_color=delta_color)

        st.markdown("<div style=\"height:20px\"></div>", unsafe_allow_html=True)

        # --- Benchmark Comparison ---
        st.markdown('<div class="section-label">Benchmark Comparison</div>', unsafe_allow_html=True)
        with st.container(border=True):
            fig_bm = go.Figure()
            fig_bm.add_trace(go.Scatter(x=df.index, y=df['Benchmark'], name=f"Benchmark ({bm_name})", line=dict(width=2, color='#94A3B8', dash='dot')))
            fig_bm.add_trace(go.Scatter(x=df.index, y=df['Portfolio'], name='Portfolio', line=dict(width=3, color='#0F172A')))
            fig_bm.update_layout(template='plotly_white', margin=dict(t=20, b=20), hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_bm, use_container_width=True)

        st.markdown("<div style=\"height:20px\"></div>", unsafe_allow_html=True)

        # --- Asset Breakdown ---
        st.markdown('<div class="section-label">Asset Breakdown</div>', unsafe_allow_html=True)
        with st.container(border=True):
            fig_assets = go.Figure()
            asset_cols = [c for c in df.columns if c not in ['Daily_Ret', 'Portfolio', 'Benchmark', 'BM_Daily_Ret']]
            palette = px.colors.qualitative.Plotly
            for i, col in enumerate(asset_cols):
                fig_assets.add_trace(go.Scatter(x=df.index, y=df[col], name=col, line=dict(width=1.5, color=palette[i % len(palette)]), opacity=0.7))
            fig_assets.add_trace(go.Scatter(x=df.index, y=df['Portfolio'], name='Portfolio', line=dict(width=4, color='#0F172A'), opacity=1.0))
            fig_assets.update_layout(template='plotly_white', margin=dict(t=20, b=20), hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_assets, use_container_width=True)

        st.markdown("<div style=\"height:20px\"></div>", unsafe_allow_html=True)

        # --- Yearly Returns ---
        st.markdown('<div class="section-label">Yearly Returns</div>', unsafe_allow_html=True)
        with st.container(border=True):
            target_cols = ['Portfolio'] + asset_cols
            daily_rets_all = df[target_cols].pct_change().dropna()
            yearly_rets_all = daily_rets_all.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
            years = yearly_rets_all.index.strftime('%Y').tolist()
            assets_y = yearly_rets_all.columns.tolist()
            if 'Portfolio' in assets_y:
                assets_y.remove('Portfolio')
                assets_y.append('Portfolio')
            # 재정렬된 순서에 맞게 데이터 가져오기
            z_val = yearly_rets_all[assets_y].T.values
            fig_heat = go.Figure(data=go.Heatmap(z=z_val, x=years, y=assets_y, colorscale='RdYlGn', zmid=0, text=np.round(z_val, 1), texttemplate="%{text}%"))
            fig_heat.update_layout(template='plotly_white', margin=dict(t=20, b=20), height=100 + (len(assets_y) * 40))
            st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("<div style=\"height:20px\"></div>", unsafe_allow_html=True)

        # --- Correlation ---
        st.markdown('<div class="section-label">Correlation</div>', unsafe_allow_html=True)
        with st.container(border=True):
            if len(asset_cols) > 1:
                # 자산 간 상관관계 계산
                corr_df = df[asset_cols].pct_change().dropna().corr()
                # 히트맵 생성 (x축과 y축이 동일한 자산 목록)
                fig_corr = go.Figure(data=go.Heatmap(
                    z=corr_df.values,
                    x=corr_df.columns,
                    y=corr_df.index,
                    colorscale='RdBu',
                    zmin=-1,
                    zmax=1,
                    text=np.round(corr_df.values, 2),
                    texttemplate="%{text}",
                    hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.2f}<extra></extra>'
                ))
                fig_corr.update_layout(
                    template='plotly_white',
                    height=max(400, len(asset_cols) * 50),
                    xaxis={'side': 'bottom'},
                    yaxis={'autorange': 'reversed'}
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("자산이 2개 이상이어야 상관관계를 확인할 수 있습니다.")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### AI Investment Analyst")
            api_key = GEMINI_API_KEY
            if not api_key:
                api_key = st.text_input("Gemini API Key", type="password", placeholder="API Key 입력")
            if st.button("Generate Analysis Report", type="secondary", use_container_width=True):
                if not api_key:
                    st.warning("API Key가 필요합니다.")
                else:
                    with st.spinner("AI analyzing..."):
                        analysis = generate_ai_analysis(st.session_state.portfolio, pm[0], pm[1], pm[2], pm[4], api_key)
                        st.session_state.ai_analysis = analysis
        if st.session_state.ai_analysis:
            st.markdown(f"""<div style="margin-top:15px; background:white; padding:25px; border-radius:10px; border:1px solid #E2E8F0; line-height:1.6; font-size:15px;">{st.session_state.ai_analysis}</div>""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 메인 화면: Technical Analysis
# ---------------------------------------------------------
elif st.session_state.selected_menu == "Technical Analysis":
    render_technical_analysis()


# ---------------------------------------------------------
# 메인 화면: Admin Panel
# ---------------------------------------------------------
elif st.session_state.selected_menu == "Admin Panel":
    st.markdown("<h1 style=\"font-size: 28px; font-weight: 700; margin-bottom: 10px;\">Admin Panel</h1>", unsafe_allow_html=True)
    st.markdown("<div style=\"height:20px;\"></div>", unsafe_allow_html=True)
    render_admin_panel()
