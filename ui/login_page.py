import streamlit as st
from auth.authentication import authenticate_user, register_user
from auth.session import login_user


def render_login_page():
    """로그인/회원가입 페이지 렌더링"""

    # 중앙 정렬을 위한 레이아웃
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
            <div style="text-align: center; margin-top: 100px; margin-bottom: 40px;">
                <h1 style="font-size: 32px; font-weight: 700; color: #1E293B;">Invest Lab</h1>
                <p style="color: #64748B; font-size: 14px;">로그인하여 포트폴리오 관리를 시작하세요</p>
            </div>
        """, unsafe_allow_html=True)

        # 로그인/회원가입 탭
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        with tab_login:
            render_login_form()

        with tab_signup:
            render_signup_form()


def render_login_form():
    """로그인 폼"""
    with st.form("login_form", clear_on_submit=False):
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="사용자명 입력", key="login_username")
        password = st.text_input("Password", type="password", placeholder="비밀번호 입력", key="login_password")

        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

        submit_button = st.form_submit_button("Login", use_container_width=True)

        if submit_button:
            if not username or not password:
                st.error("사용자명과 비밀번호를 입력하세요.")
            else:
                user = authenticate_user(username, password)
                if user:
                    login_user(user)
                    st.success("로그인 성공!")
                    st.rerun()
                else:
                    st.error("사용자명 또는 비밀번호가 올바르지 않습니다.")


def render_signup_form():
    """회원가입 폼"""
    with st.form("signup_form", clear_on_submit=False):
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="사용자명 입력 (3-20자, 영문/숫자/언더스코어)", key="signup_username")
        password = st.text_input("Password", type="password", placeholder="비밀번호 입력 (최소 8자)", key="signup_password")
        password_confirm = st.text_input("Confirm Password", type="password", placeholder="비밀번호 확인", key="signup_password_confirm")

        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

        submit_button = st.form_submit_button("Register", use_container_width=True)

        if submit_button:
            if not username or not password or not password_confirm:
                st.error("모든 필드를 입력하세요.")
            elif password != password_confirm:
                st.error("비밀번호가 일치하지 않습니다.")
            else:
                success, result = register_user(username, password)
                if success:
                    st.success("회원가입 성공! 자동으로 로그인됩니다.")
                    # 자동 로그인
                    user = authenticate_user(username, password)
                    if user:
                        login_user(user)
                        st.rerun()
                else:
                    st.error(result)
