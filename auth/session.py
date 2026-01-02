"""세션 관리 모듈"""

import streamlit as st


# 앱에서 사용하는 모든 세션 상태 키 정의
SESSION_DEFAULTS = {
    # 인증 관련
    'authenticated': False,
    'user': None,
    # 포트폴리오 관련
    'portfolio': [],
    'sim_result': None,
    'ai_analysis': None,
    # UI 상태
    'search_result': None,
    'selected_menu': "Portfolio Backtest",
    # Technical Analysis 관련
    'ta_data': None,
    'ta_ticker': None,
    'ta_name': None,
    'ta_currency': None,
    'ta_period': '1y',
    'ta_interval': '1d',
}


def init_session_state():
    """모든 세션 상태 초기화"""
    for key, default_value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_backtest_state():
    """백테스트 관련 상태만 초기화"""
    st.session_state.sim_result = None
    st.session_state.ai_analysis = None


def login_user(user):
    """사용자 로그인 (세션에 저장)"""
    st.session_state.authenticated = True
    st.session_state.user = {
        'user_id': user['user_id'],
        'username': user['username'],
        'is_admin': bool(user['is_admin'])
    }


def logout_user():
    """사용자 로그아웃 (세션 초기화)"""
    st.session_state.authenticated = False
    st.session_state.user = None
    # 포트폴리오 상태도 초기화
    st.session_state.portfolio = []
    st.session_state.sim_result = None
    st.session_state.ai_analysis = None


def is_authenticated():
    """로그인 여부 확인"""
    return st.session_state.get('authenticated', False)


def is_admin():
    """관리자 권한 확인"""
    if not is_authenticated():
        return False

    user = st.session_state.get('user')
    if not user:
        return False

    return user.get('is_admin', False)


def get_current_user():
    """현재 로그인한 사용자 정보 반환"""
    if not is_authenticated():
        return None

    return st.session_state.get('user')
