"""통합 종목 검색 컴포넌트"""

import streamlit as st
import yfinance as yf

from auth.session import get_current_user
from db.models import (
    get_user_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
    is_in_watchlist
)
from core.data_fetcher import search_ticker, search_by_keyword

# 최근 검색 최대 개수
MAX_RECENT_SEARCHES = 5

# 주요 종목 리스트 (종목명 검색용) - 한글 키워드 강화
POPULAR_STOCKS = [
    # 미국 주요 종목
    {"ticker": "AAPL", "name": "Apple Inc.", "keywords": ["애플", "apple", "아이폰", "iphone", "맥", "mac"], "currency": "USD"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "keywords": ["마이크로소프트", "microsoft", "ms", "윈도우", "windows", "엠에스"], "currency": "USD"},
    {"ticker": "GOOGL", "name": "Alphabet (Google)", "keywords": ["구글", "google", "알파벳", "alphabet", "유튜브", "youtube"], "currency": "USD"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "keywords": ["아마존", "amazon", "aws"], "currency": "USD"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "keywords": ["테슬라", "tesla", "일론머스크", "전기차"], "currency": "USD"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "keywords": ["엔비디아", "nvidia", "nvda", "그래픽카드", "gpu"], "currency": "USD"},
    {"ticker": "META", "name": "Meta Platforms", "keywords": ["메타", "meta", "페이스북", "facebook", "인스타그램", "instagram"], "currency": "USD"},
    {"ticker": "NFLX", "name": "Netflix Inc.", "keywords": ["넷플릭스", "netflix", "넷플"], "currency": "USD"},
    {"ticker": "AMD", "name": "AMD Inc.", "keywords": ["amd", "에이엠디", "암드", "라이젠", "ryzen"], "currency": "USD"},
    {"ticker": "INTC", "name": "Intel Corp.", "keywords": ["인텔", "intel"], "currency": "USD"},
    {"ticker": "CRM", "name": "Salesforce Inc.", "keywords": ["세일즈포스", "salesforce"], "currency": "USD"},
    {"ticker": "ORCL", "name": "Oracle Corp.", "keywords": ["오라클", "oracle"], "currency": "USD"},
    {"ticker": "CSCO", "name": "Cisco Systems", "keywords": ["시스코", "cisco"], "currency": "USD"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "keywords": ["어도비", "adobe", "포토샵", "photoshop"], "currency": "USD"},
    {"ticker": "PYPL", "name": "PayPal Holdings", "keywords": ["페이팔", "paypal"], "currency": "USD"},
    {"ticker": "DIS", "name": "Walt Disney Co.", "keywords": ["디즈니", "disney", "월트디즈니"], "currency": "USD"},
    {"ticker": "V", "name": "Visa Inc.", "keywords": ["비자", "visa", "비자카드"], "currency": "USD"},
    {"ticker": "MA", "name": "Mastercard Inc.", "keywords": ["마스터카드", "mastercard"], "currency": "USD"},
    {"ticker": "JPM", "name": "JPMorgan Chase", "keywords": ["제이피모건", "jpmorgan", "jp모건"], "currency": "USD"},
    {"ticker": "BAC", "name": "Bank of America", "keywords": ["뱅크오브아메리카", "boa", "뱅오아"], "currency": "USD"},
    {"ticker": "WMT", "name": "Walmart Inc.", "keywords": ["월마트", "walmart"], "currency": "USD"},
    {"ticker": "KO", "name": "Coca-Cola Co.", "keywords": ["코카콜라", "cocacola", "coca-cola", "콜라"], "currency": "USD"},
    {"ticker": "PEP", "name": "PepsiCo Inc.", "keywords": ["펩시", "pepsi", "pepsico", "펩시콜라"], "currency": "USD"},
    {"ticker": "MCD", "name": "McDonald's Corp.", "keywords": ["맥도날드", "mcdonalds", "맥날", "맥도"], "currency": "USD"},
    {"ticker": "NKE", "name": "Nike Inc.", "keywords": ["나이키", "nike"], "currency": "USD"},
    {"ticker": "BA", "name": "Boeing Co.", "keywords": ["보잉", "boeing"], "currency": "USD"},
    {"ticker": "XOM", "name": "Exxon Mobil", "keywords": ["엑손모빌", "exxon", "엑손"], "currency": "USD"},
    {"ticker": "CVX", "name": "Chevron Corp.", "keywords": ["셰브론", "chevron"], "currency": "USD"},
    {"ticker": "COST", "name": "Costco Wholesale", "keywords": ["코스트코", "costco"], "currency": "USD"},
    {"ticker": "UNH", "name": "UnitedHealth Group", "keywords": ["유나이티드헬스", "unitedhealth"], "currency": "USD"},
    {"ticker": "PG", "name": "Procter & Gamble", "keywords": ["피앤지", "p&g", "프록터앤갬블"], "currency": "USD"},
    {"ticker": "HD", "name": "Home Depot", "keywords": ["홈디포", "homedepot"], "currency": "USD"},
    # 미국 ETF
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF", "keywords": ["spy", "s&p500", "s&p 500", "스파이", "에스앤피"], "currency": "USD"},
    {"ticker": "QQQ", "name": "Invesco QQQ Trust", "keywords": ["qqq", "나스닥", "nasdaq", "큐큐큐"], "currency": "USD"},
    {"ticker": "IWM", "name": "iShares Russell 2000", "keywords": ["iwm", "러셀", "russell", "러셀2000"], "currency": "USD"},
    {"ticker": "GLD", "name": "SPDR Gold Shares", "keywords": ["gld", "금", "gold", "골드"], "currency": "USD"},
    {"ticker": "SLV", "name": "iShares Silver Trust", "keywords": ["slv", "은", "silver", "실버"], "currency": "USD"},
    {"ticker": "TLT", "name": "iShares 20+ Year Treasury", "keywords": ["tlt", "국채", "treasury", "미국국채"], "currency": "USD"},
    {"ticker": "VTI", "name": "Vanguard Total Stock Market", "keywords": ["vti", "뱅가드", "vanguard"], "currency": "USD"},
    {"ticker": "VOO", "name": "Vanguard S&P 500", "keywords": ["voo", "뱅가드sp500"], "currency": "USD"},
    {"ticker": "ARKK", "name": "ARK Innovation ETF", "keywords": ["arkk", "아크", "ark", "캐시우드"], "currency": "USD"},
    {"ticker": "SCHD", "name": "Schwab US Dividend", "keywords": ["schd", "슈드", "배당etf"], "currency": "USD"},
    {"ticker": "SOXL", "name": "Direxion Semiconductor Bull 3X", "keywords": ["soxl", "반도체3배", "반도체레버리지"], "currency": "USD"},
    {"ticker": "TQQQ", "name": "ProShares UltraPro QQQ", "keywords": ["tqqq", "나스닥3배", "3배레버리지"], "currency": "USD"},
    # 한국 주요 종목 (KOSPI)
    {"ticker": "005930.KS", "name": "삼성전자", "keywords": ["삼성전자", "samsung", "삼성", "samsung electronics", "반도체"], "currency": "KRW"},
    {"ticker": "000660.KS", "name": "SK하이닉스", "keywords": ["sk하이닉스", "하이닉스", "skhynix", "sk 하이닉스", "에스케이하이닉스"], "currency": "KRW"},
    {"ticker": "373220.KS", "name": "LG에너지솔루션", "keywords": ["lg에너지솔루션", "엘지에너지", "lg에너지", "에너지솔루션", "배터리"], "currency": "KRW"},
    {"ticker": "207940.KS", "name": "삼성바이오로직스", "keywords": ["삼성바이오", "삼바", "삼성바이오로직스", "바이오로직스"], "currency": "KRW"},
    {"ticker": "005380.KS", "name": "현대차", "keywords": ["현대차", "현대자동차", "hyundai", "현대", "현차"], "currency": "KRW"},
    {"ticker": "006400.KS", "name": "삼성SDI", "keywords": ["삼성sdi", "sdi", "삼성에스디아이", "에스디아이"], "currency": "KRW"},
    {"ticker": "051910.KS", "name": "LG화학", "keywords": ["lg화학", "엘지화학", "lg 화학", "엘지 화학"], "currency": "KRW"},
    {"ticker": "035420.KS", "name": "NAVER", "keywords": ["네이버", "naver", "nhn", "네이바"], "currency": "KRW"},
    {"ticker": "000270.KS", "name": "기아", "keywords": ["기아", "기아차", "kia", "기아자동차"], "currency": "KRW"},
    {"ticker": "035720.KS", "name": "카카오", "keywords": ["카카오", "kakao", "카톡", "카카오톡"], "currency": "KRW"},
    {"ticker": "005490.KS", "name": "POSCO홀딩스", "keywords": ["포스코", "posco", "포스코홀딩스", "포철"], "currency": "KRW"},
    {"ticker": "028260.KS", "name": "삼성물산", "keywords": ["삼성물산", "삼물"], "currency": "KRW"},
    {"ticker": "105560.KS", "name": "KB금융", "keywords": ["kb금융", "국민은행", "kb", "케이비금융", "국민금융"], "currency": "KRW"},
    {"ticker": "055550.KS", "name": "신한지주", "keywords": ["신한지주", "신한은행", "신한", "신한금융"], "currency": "KRW"},
    {"ticker": "066570.KS", "name": "LG전자", "keywords": ["lg전자", "엘지전자", "lg 전자", "엘지 전자"], "currency": "KRW"},
    {"ticker": "012330.KS", "name": "현대모비스", "keywords": ["현대모비스", "모비스", "hyundai mobis"], "currency": "KRW"},
    {"ticker": "003550.KS", "name": "LG", "keywords": ["lg", "엘지", "엘쥐"], "currency": "KRW"},
    {"ticker": "034730.KS", "name": "SK", "keywords": ["sk", "에스케이", "sk 지주"], "currency": "KRW"},
    {"ticker": "096770.KS", "name": "SK이노베이션", "keywords": ["sk이노베이션", "sk이노", "에스케이이노베이션"], "currency": "KRW"},
    {"ticker": "017670.KS", "name": "SK텔레콤", "keywords": ["sk텔레콤", "skt", "에스케이텔레콤", "sk 텔레콤"], "currency": "KRW"},
    {"ticker": "030200.KS", "name": "KT", "keywords": ["kt", "케이티", "한국통신"], "currency": "KRW"},
    {"ticker": "032830.KS", "name": "삼성생명", "keywords": ["삼성생명", "삼생"], "currency": "KRW"},
    {"ticker": "086790.KS", "name": "하나금융지주", "keywords": ["하나금융", "하나은행", "하나", "하나금융지주"], "currency": "KRW"},
    {"ticker": "009150.KS", "name": "삼성전기", "keywords": ["삼성전기", "삼전기"], "currency": "KRW"},
    {"ticker": "018260.KS", "name": "삼성에스디에스", "keywords": ["삼성sds", "삼성에스디에스", "에스디에스", "sds"], "currency": "KRW"},
    {"ticker": "003670.KS", "name": "포스코퓨처엠", "keywords": ["포스코퓨처엠", "포스코케미칼", "posco퓨처엠"], "currency": "KRW"},
    {"ticker": "000810.KS", "name": "삼성화재", "keywords": ["삼성화재", "삼화"], "currency": "KRW"},
    {"ticker": "033780.KS", "name": "KT&G", "keywords": ["kt&g", "케이티앤지", "담배인삼공사"], "currency": "KRW"},
    {"ticker": "010950.KS", "name": "S-Oil", "keywords": ["에스오일", "s-oil", "s oil", "에쓰오일"], "currency": "KRW"},
    {"ticker": "024110.KS", "name": "기업은행", "keywords": ["기업은행", "ibk", "아이비케이"], "currency": "KRW"},
    {"ticker": "015760.KS", "name": "한국전력", "keywords": ["한국전력", "한전", "kepco", "전력공사"], "currency": "KRW"},
    {"ticker": "090430.KS", "name": "아모레퍼시픽", "keywords": ["아모레퍼시픽", "아모레", "amore"], "currency": "KRW"},
    {"ticker": "047050.KS", "name": "포스코인터내셔널", "keywords": ["포스코인터내셔널", "포스코인터"], "currency": "KRW"},
    {"ticker": "316140.KS", "name": "우리금융지주", "keywords": ["우리금융", "우리은행", "우리금융지주"], "currency": "KRW"},
    {"ticker": "010130.KS", "name": "고려아연", "keywords": ["고려아연", "아연"], "currency": "KRW"},
    {"ticker": "006800.KS", "name": "미래에셋증권", "keywords": ["미래에셋증권", "미래에셋", "미에셋"], "currency": "KRW"},
    {"ticker": "000720.KS", "name": "현대건설", "keywords": ["현대건설", "현건"], "currency": "KRW"},
    {"ticker": "034020.KS", "name": "두산에너빌리티", "keywords": ["두산에너빌리티", "두산중공업", "두에너"], "currency": "KRW"},
    {"ticker": "068270.KS", "name": "셀트리온", "keywords": ["셀트리온", "celltrion", "셀트"], "currency": "KRW"},
    {"ticker": "326030.KS", "name": "SK바이오팜", "keywords": ["sk바이오팜", "에스케이바이오팜", "sk 바이오팜"], "currency": "KRW"},
    {"ticker": "352820.KS", "name": "하이브", "keywords": ["하이브", "hybe", "bts", "빅히트"], "currency": "KRW"},
    {"ticker": "011200.KS", "name": "HMM", "keywords": ["hmm", "에이치엠엠", "현대상선"], "currency": "KRW"},
    # 한국 ETF
    {"ticker": "069500.KS", "name": "KODEX 200", "keywords": ["코덱스200", "kodex200", "kodex 200"], "currency": "KRW"},
    {"ticker": "229200.KS", "name": "KODEX 코스닥150", "keywords": ["코덱스코스닥", "코덱스150", "kodex코스닥"], "currency": "KRW"},
    {"ticker": "122630.KS", "name": "KODEX 레버리지", "keywords": ["코덱스레버리지", "kodex레버리지", "2배레버리지"], "currency": "KRW"},
    {"ticker": "252670.KS", "name": "KODEX 200선물인버스2X", "keywords": ["코덱스인버스", "곱버스", "인버스2배"], "currency": "KRW"},
    # 일본 주요 종목
    {"ticker": "7203.T", "name": "Toyota Motor", "keywords": ["토요타", "toyota", "도요타", "도요다"], "currency": "JPY"},
    {"ticker": "6758.T", "name": "Sony Group", "keywords": ["소니", "sony", "소니그룹"], "currency": "JPY"},
    {"ticker": "9984.T", "name": "SoftBank Group", "keywords": ["소프트뱅크", "softbank", "손정의"], "currency": "JPY"},
    {"ticker": "6861.T", "name": "Keyence Corp.", "keywords": ["키엔스", "keyence"], "currency": "JPY"},
    {"ticker": "8306.T", "name": "Mitsubishi UFJ", "keywords": ["미쓰비시", "mitsubishi", "미츠비시"], "currency": "JPY"},
    {"ticker": "6501.T", "name": "Hitachi Ltd.", "keywords": ["히타치", "hitachi"], "currency": "JPY"},
    {"ticker": "7267.T", "name": "Honda Motor", "keywords": ["혼다", "honda"], "currency": "JPY"},
    {"ticker": "9432.T", "name": "NTT Corp.", "keywords": ["ntt", "엔티티", "일본전신전화"], "currency": "JPY"},
    {"ticker": "4502.T", "name": "Takeda Pharma", "keywords": ["타케다", "takeda", "다케다"], "currency": "JPY"},
    {"ticker": "7974.T", "name": "Nintendo Co.", "keywords": ["닌텐도", "nintendo", "임천당"], "currency": "JPY"},
    {"ticker": "6902.T", "name": "Denso Corp.", "keywords": ["덴소", "denso"], "currency": "JPY"},
    {"ticker": "4568.T", "name": "Daiichi Sankyo", "keywords": ["다이이치산쿄", "daiichi"], "currency": "JPY"},
    {"ticker": "9433.T", "name": "KDDI Corp.", "keywords": ["kddi", "케이디디아이"], "currency": "JPY"},
    {"ticker": "6954.T", "name": "Fanuc Corp.", "keywords": ["화낙", "fanuc", "파낙"], "currency": "JPY"},
]


def init_search_session():
    """검색 관련 세션 상태 초기화"""
    if 'recent_searches' not in st.session_state:
        st.session_state.recent_searches = []


def add_to_recent_searches(ticker: str, name: str, currency: str):
    """최근 검색 목록에 추가"""
    init_search_session()

    # 중복 제거
    st.session_state.recent_searches = [
        s for s in st.session_state.recent_searches
        if s['ticker'] != ticker
    ]

    # 맨 앞에 추가
    st.session_state.recent_searches.insert(0, {
        'ticker': ticker,
        'name': name,
        'currency': currency
    })

    # 최대 개수 유지
    st.session_state.recent_searches = st.session_state.recent_searches[:MAX_RECENT_SEARCHES]


def search_by_name(query: str, limit: int = 5) -> list:
    """
    종목명/키워드로 검색 (POPULAR_STOCKS에서)

    Args:
        query: 검색어
        limit: 최대 결과 수

    Returns:
        list: [{'ticker': str, 'name': str, 'currency': str}, ...]
    """
    query_lower = query.lower().strip()
    results = []

    for stock in POPULAR_STOCKS:
        # 티커 매칭
        if query_lower == stock['ticker'].lower():
            results.append({
                'ticker': stock['ticker'],
                'name': stock['name'],
                'currency': stock['currency']
            })
            continue

        # 종목명 매칭
        if query_lower in stock['name'].lower():
            results.append({
                'ticker': stock['ticker'],
                'name': stock['name'],
                'currency': stock['currency']
            })
            continue

        # 키워드 매칭
        for keyword in stock['keywords']:
            if query_lower in keyword.lower() or keyword.lower() in query_lower:
                results.append({
                    'ticker': stock['ticker'],
                    'name': stock['name'],
                    'currency': stock['currency']
                })
                break

    return results[:limit]


def search_stocks(query: str, limit: int = 5) -> list:
    """
    종목 검색 (티커 또는 종목명)

    Args:
        query: 검색어
        limit: 최대 결과 수

    Returns:
        list: [{'ticker': str, 'name': str, 'currency': str}, ...]
    """
    if not query or len(query) < 1:
        return []

    results = []
    added_tickers = set()

    # 1. 종목명/키워드로 검색 (POPULAR_STOCKS에서)
    name_results = search_by_name(query, limit)
    for stock in name_results:
        if stock['ticker'] not in added_tickers:
            results.append(stock)
            added_tickers.add(stock['ticker'])

    # 2. 직접 티커 검색 (yfinance)
    if len(results) < limit:
        found, ticker, name, currency = search_ticker(query)
        if found and ticker not in added_tickers:
            results.append({
                'ticker': ticker,
                'name': name,
                'currency': currency
            })
            added_tickers.add(ticker)

    # 3. yfinance Search로 종목명 검색 (POPULAR_STOCKS에 없는 종목도 검색)
    if len(results) < limit:
        yf_results = search_by_keyword(query, limit - len(results))
        for stock in yf_results:
            if stock['ticker'] not in added_tickers:
                results.append(stock)
                added_tickers.add(stock['ticker'])

    return results[:limit]


def render_stock_search(
    key_prefix: str,
    on_select: callable = None,
    show_watchlist: bool = True,
    show_recent: bool = True,
    placeholder: str = "Search by ticker or name (e.g. AAPL, 삼성전자, 005930)"
):
    """
    통합 종목 검색 UI 렌더링

    Args:
        key_prefix: Streamlit 위젯 키 접두사 (고유해야 함)
        on_select: 종목 선택 시 콜백 함수 (ticker, name, currency를 인자로 받음)
        show_watchlist: Watchlist 표시 여부
        show_recent: 최근 검색 표시 여부
        placeholder: 검색창 placeholder

    Returns:
        dict or None: 선택된 종목 {'ticker', 'name', 'currency'} 또는 None
    """
    init_search_session()
    user = get_current_user()
    selected_stock = None

    # 검색창
    st.markdown('<div class="section-label">Search Stock</div>', unsafe_allow_html=True)

    col_search, col_btn = st.columns([3, 1])

    with col_search:
        search_query = st.text_input(
            "Search",
            placeholder=placeholder,
            label_visibility="collapsed",
            key=f"{key_prefix}_search_input"
        )

    with col_btn:
        search_clicked = st.button("Search", key=f"{key_prefix}_search_btn", use_container_width=True)

    # 검색 결과
    if search_clicked and search_query:
        results = search_stocks(search_query)
        if results:
            st.session_state[f"{key_prefix}_search_results"] = results
        else:
            st.warning("No results found.")
            st.session_state[f"{key_prefix}_search_results"] = []

    # 검색 결과 표시
    if st.session_state.get(f"{key_prefix}_search_results"):
        results = st.session_state[f"{key_prefix}_search_results"]
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

        for i, stock in enumerate(results):
            col_info, col_select, col_watch = st.columns([2.5, 1, 0.5])

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
                if st.button("Select", key=f"{key_prefix}_select_{i}", use_container_width=True):
                    selected_stock = stock
                    add_to_recent_searches(stock['ticker'], stock['name'], stock['currency'])
                    st.session_state[f"{key_prefix}_search_results"] = []
                    if on_select:
                        on_select(stock['ticker'], stock['name'], stock['currency'])

            with col_watch:
                if user:
                    in_watchlist = is_in_watchlist(user['user_id'], stock['ticker'])
                    btn_label = "★" if in_watchlist else "☆"
                    if st.button(btn_label, key=f"{key_prefix}_watch_{i}", use_container_width=True):
                        if in_watchlist:
                            remove_from_watchlist(user['user_id'], stock['ticker'])
                        else:
                            add_to_watchlist(user['user_id'], stock['ticker'], stock['name'], stock['currency'])
                        st.rerun()

    st.markdown('<div style="height:15px;"></div>', unsafe_allow_html=True)

    # 최근 검색 & Watchlist를 나란히 표시
    col_recent, col_watchlist = st.columns(2)

    # 최근 검색
    if show_recent:
        with col_recent:
            recent = st.session_state.get('recent_searches', [])
            if recent:
                st.markdown('<div class="section-label">Recent</div>', unsafe_allow_html=True)
                cols = st.columns(min(len(recent), 5))
                for i, stock in enumerate(recent[:5]):
                    with cols[i]:
                        if st.button(
                            stock['ticker'],
                            key=f"{key_prefix}_recent_{i}",
                            use_container_width=True
                        ):
                            selected_stock = stock
                            if on_select:
                                on_select(stock['ticker'], stock['name'], stock['currency'])

    # Watchlist
    if show_watchlist and user:
        with col_watchlist:
            watchlist = get_user_watchlist(user['user_id'])
            if watchlist:
                st.markdown('<div class="section-label">★ Watchlist</div>', unsafe_allow_html=True)
                # 최대 5개만 표시
                display_list = watchlist[:5]
                cols = st.columns(min(len(display_list), 5))
                for i, stock in enumerate(display_list):
                    with cols[i]:
                        if st.button(
                            stock['ticker'],
                            key=f"{key_prefix}_watchlist_{i}",
                            use_container_width=True
                        ):
                            selected_stock = {
                                'ticker': stock['ticker'],
                                'name': stock['name'],
                                'currency': stock['currency']
                            }
                            add_to_recent_searches(stock['ticker'], stock['name'], stock['currency'])
                            if on_select:
                                on_select(stock['ticker'], stock['name'], stock['currency'])

    return selected_stock


def render_watchlist_manager():
    """Watchlist 관리 UI (전체 목록 + 삭제)"""
    user = get_current_user()
    if not user:
        return

    watchlist = get_user_watchlist(user['user_id'])

    st.markdown('<div class="section-label">★ Watchlist Management</div>', unsafe_allow_html=True)

    if not watchlist:
        st.caption("No items in watchlist. Search and add stocks using ☆ button.")
        return

    for stock in watchlist:
        col_info, col_del = st.columns([4, 1])

        with col_info:
            st.markdown(
                f"<div style='padding:6px 0;'>"
                f"<span style='font-weight:600;'>{stock['ticker']}</span> "
                f"<span style='color:#64748B; font-size:13px;'>{stock['name'] or ''}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

        with col_del:
            if st.button("Remove", key=f"wl_remove_{stock['ticker']}", use_container_width=True):
                remove_from_watchlist(user['user_id'], stock['ticker'])
                st.rerun()
