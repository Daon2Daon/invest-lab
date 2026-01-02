import streamlit as st
from db.models import get_all_users, get_all_portfolios, delete_user, delete_portfolio_by_id
from auth.session import get_current_user


def render_admin_panel():
    """관리자 패널 렌더링"""

    st.markdown("### 사용자 관리")

    # 사용자 목록
    users = get_all_users()
    if users:
        st.markdown(f"**총 사용자 수:** {len(users)}")

        for user in users:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

            with col1:
                admin_badge = " (Admin)" if user['is_admin'] else ""
                st.markdown(f"**{user['username']}**{admin_badge}")

            with col2:
                st.caption(f"가입: {user['created_at'][:10] if user.get('created_at') else 'N/A'}")

            with col3:
                if user['is_admin']:
                    st.caption("관리자")
                else:
                    st.caption("")

            with col4:
                # 관리자 계정은 삭제 불가
                if not user['is_admin']:
                    if st.button("Del", key=f"del_user_{user['user_id']}", use_container_width=True):
                        if delete_user(user['user_id']):
                            st.success(f"사용자 '{user['username']}'이(가) 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("삭제 실패")

        st.markdown("---")
    else:
        st.caption("사용자가 없습니다.")

    st.markdown("### 전략 관리")

    # 포트폴리오 목록
    portfolios = get_all_portfolios()
    if portfolios:
        st.markdown(f"**총 전략 수:** {len(portfolios)}")

        for portfolio in portfolios:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                st.markdown(f"**{portfolio['portfolio_name']}**")

            with col2:
                st.caption(f"사용자: {portfolio['username']}")

            with col3:
                st.caption(f"수정: {portfolio['updated_at'][:10] if portfolio.get('updated_at') else 'N/A'}")

            with col4:
                if st.button("Del", key=f"del_portfolio_{portfolio['portfolio_id']}", use_container_width=True):
                    if delete_portfolio_by_id(portfolio['portfolio_id']):
                        st.success(f"전략 '{portfolio['portfolio_name']}'이(가) 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("삭제 실패")

        st.markdown("---")
    else:
        st.caption("저장된 전략이 없습니다.")
