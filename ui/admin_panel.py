import streamlit as st
from datetime import datetime
from db.models import get_all_users, get_all_portfolios, delete_user, delete_portfolio_by_id
from utils.backup_manager import (
    create_backup, list_backups, restore_backup, delete_backup,
    save_uploaded_backup, format_file_size
)
from utils.system_monitor import (
    get_database_stats, get_user_stats, get_portfolio_stats,
    get_watchlist_stats, get_stock_notes_stats, get_backup_stats,
    format_bytes
)
from utils.data_exporter import (
    export_portfolios_to_csv, export_portfolios_to_json,
    export_watchlist_to_csv, export_stock_notes_to_csv,
    export_all_data_to_zip,
    import_portfolios_from_csv, import_watchlist_from_csv,
    import_stock_notes_from_csv, validate_csv_format
)


def render_admin_panel():
    """관리자 패널 렌더링"""

    st.markdown("## Admin Panel")
    st.markdown("---")

    # 탭 생성
    tabs = st.tabs([
        "대시보드",
        "백업 및 복원",
        "데이터 관리",
        "사용자 관리",
        "전략 관리"
    ])

    # 각 탭 렌더링
    with tabs[0]:
        render_dashboard()

    with tabs[1]:
        render_backup_section()

    with tabs[2]:
        render_data_management()

    with tabs[3]:
        render_user_management()

    with tabs[4]:
        render_portfolio_management()


# ==================================================
# 대시보드
# ==================================================

def render_dashboard():
    """시스템 대시보드"""

    st.markdown("### 시스템 개요")

    # 통계 수집
    db_stats = get_database_stats()
    user_stats = get_user_stats()
    portfolio_stats = get_portfolio_stats()
    watchlist_stats = get_watchlist_stats()
    notes_stats = get_stock_notes_stats()
    backup_stats = get_backup_stats()

    # 주요 지표 카드 (4열)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="총 사용자",
            value=f"{user_stats['total_users']}명",
            delta=f"관리자 {user_stats['admin_count']}명"
        )

    with col2:
        st.metric(
            label="포트폴리오",
            value=f"{portfolio_stats['total_portfolios']}개",
            delta=f"평균 {portfolio_stats['avg_per_user']}개/사용자"
        )

    with col3:
        st.metric(
            label="데이터베이스",
            value=format_bytes(db_stats['db_size']),
            delta=f"{db_stats['total_records']} 레코드"
        )

    with col4:
        st.metric(
            label="백업",
            value=f"{backup_stats['count']}개",
            delta=format_bytes(backup_stats['total_size']) if backup_stats['count'] > 0 else "없음"
        )

    st.markdown("---")

    # 상세 통계 (2열)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 데이터 현황")
        st.markdown(f"- **관심종목**: {watchlist_stats['total_watchlist']}개")
        st.markdown(f"- **종목 메모**: {notes_stats['total_notes']}개")
        st.markdown(f"- **DB 경로**: `{db_stats['db_path']}`")

        if backup_stats['latest_backup']:
            latest_backup_str = backup_stats['latest_backup'].strftime('%Y-%m-%d %H:%M')
            st.markdown(f"- **최근 백업**: {latest_backup_str}")
        else:
            st.markdown(f"- **최근 백업**: 없음")

    with col2:
        st.markdown("#### 활동 현황")

        if user_stats['latest_user']['username']:
            st.markdown(f"- **최근 가입**: {user_stats['latest_user']['username']} ({user_stats['latest_user']['created_at'][:10] if user_stats['latest_user']['created_at'] else 'N/A'})")
        else:
            st.markdown(f"- **최근 가입**: 없음")

        if user_stats['latest_login']['username']:
            st.markdown(f"- **최근 로그인**: {user_stats['latest_login']['username']} ({user_stats['latest_login']['last_login'][:16] if user_stats['latest_login']['last_login'] else 'N/A'})")
        else:
            st.markdown(f"- **최근 로그인**: 없음")

        if portfolio_stats['latest_portfolio']['name']:
            st.markdown(f"- **최근 수정 전략**: {portfolio_stats['latest_portfolio']['name']} ({portfolio_stats['latest_portfolio']['updated_at'][:10] if portfolio_stats['latest_portfolio']['updated_at'] else 'N/A'})")
        else:
            st.markdown(f"- **최근 수정 전략**: 없음")


# ==================================================
# 백업 및 복원
# ==================================================

def render_backup_section():
    """백업 및 복원 섹션"""

    st.markdown("### 백업 및 복원")

    # 백업 생성 버튼
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("지금 백업 생성", type="primary", use_container_width=True):
            with st.spinner("백업 생성 중..."):
                result = create_backup()
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])

    st.markdown("---")

    # 백업 파일 목록
    st.markdown("#### 백업 파일 목록")

    backups = list_backups()

    if not backups:
        st.info("백업 파일이 없습니다. 위의 버튼을 눌러 백업을 생성하세요.")
    else:
        st.markdown(f"**총 {len(backups)}개의 백업 파일**")

        # 테이블 헤더
        header_cols = st.columns([3, 2, 1, 1, 1, 1])
        with header_cols[0]:
            st.markdown("**파일명**")
        with header_cols[1]:
            st.markdown("**생성일시**")
        with header_cols[2]:
            st.markdown("**크기**")
        with header_cols[3]:
            st.markdown("**다운로드**")
        with header_cols[4]:
            st.markdown("**복원**")
        with header_cols[5]:
            st.markdown("**삭제**")

        st.markdown("---")

        # 백업 파일 행
        for backup in backups:
            cols = st.columns([3, 2, 1, 1, 1, 1])

            with cols[0]:
                st.text(backup['filename'])

            with cols[1]:
                st.text(backup['created_at'].strftime('%Y-%m-%d %H:%M'))

            with cols[2]:
                st.text(format_file_size(backup['size']))

            with cols[3]:
                # 다운로드 버튼
                with open(backup['filepath'], 'rb') as f:
                    st.download_button(
                        label="⬇",
                        data=f.read(),
                        file_name=backup['filename'],
                        mime="application/octet-stream",
                        key=f"download_{backup['filename']}",
                        use_container_width=True
                    )

            with cols[4]:
                # 복원 버튼
                if st.button("♻", key=f"restore_{backup['filename']}", use_container_width=True):
                    # 확인 대화상자
                    st.session_state[f'confirm_restore_{backup["filename"]}'] = True

            with cols[5]:
                # 삭제 버튼
                if st.button("🗑", key=f"delete_{backup['filename']}", use_container_width=True):
                    st.session_state[f'confirm_delete_{backup["filename"]}'] = True

        # 복원 확인 대화상자
        for backup in backups:
            if st.session_state.get(f'confirm_restore_{backup["filename"]}'):
                st.warning(f"⚠ **'{backup['filename']}'로 복원하시겠습니까?**")
                st.markdown("현재 데이터베이스는 자동으로 백업됩니다.")

                confirm_cols = st.columns([1, 1, 2])
                with confirm_cols[0]:
                    if st.button("✓ 복원", key=f"confirm_yes_restore_{backup['filename']}", type="primary"):
                        with st.spinner("복원 중..."):
                            result = restore_backup(backup['filename'])
                            if result['success']:
                                st.success(result['message'])
                                if result.get('safety_backup'):
                                    st.info(f"안전 백업: {result['safety_backup']}")
                                del st.session_state[f'confirm_restore_{backup["filename"]}']
                                st.rerun()
                            else:
                                st.error(result['message'])
                with confirm_cols[1]:
                    if st.button("✗ 취소", key=f"confirm_no_restore_{backup['filename']}"):
                        del st.session_state[f'confirm_restore_{backup["filename"]}']
                        st.rerun()
                break

        # 삭제 확인 대화상자
        for backup in backups:
            if st.session_state.get(f'confirm_delete_{backup["filename"]}'):
                st.warning(f"⚠ **'{backup['filename']}'를 삭제하시겠습니까?**")

                confirm_cols = st.columns([1, 1, 2])
                with confirm_cols[0]:
                    if st.button("✓ 삭제", key=f"confirm_yes_delete_{backup['filename']}", type="primary"):
                        result = delete_backup(backup['filename'])
                        if result['success']:
                            st.success(result['message'])
                            del st.session_state[f'confirm_delete_{backup["filename"]}']
                            st.rerun()
                        else:
                            st.error(result['message'])
                with confirm_cols[1]:
                    if st.button("✗ 취소", key=f"confirm_no_delete_{backup['filename']}"):
                        del st.session_state[f'confirm_delete_{backup["filename"]}']
                        st.rerun()
                break

    st.markdown("---")

    # 백업 파일 업로드
    st.markdown("#### 백업 파일 업로드")
    st.caption("외부 백업 파일을 업로드하여 복원할 수 있습니다.")

    uploaded_file = st.file_uploader(
        "백업 파일 선택 (.db)",
        type=['db'],
        key='backup_upload'
    )

    if uploaded_file:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("업로드 및 저장", type="primary", use_container_width=True):
                with st.spinner("업로드 중..."):
                    result = save_uploaded_backup(uploaded_file)
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])


# ==================================================
# 데이터 관리
# ==================================================

def render_data_management():
    """데이터 내보내기 및 가져오기"""

    st.markdown("### 데이터 관리")

    # 내보내기와 가져오기를 2열로 배치
    col1, col2 = st.columns(2)

    with col1:
        render_data_export()

    with col2:
        render_data_import()


def render_data_export():
    """데이터 내보내기"""

    st.markdown("#### 데이터 내보내기")

    # 내보내기 옵션
    export_type = st.selectbox(
        "내보낼 데이터 선택",
        ["포트폴리오 (CSV)", "포트폴리오 (JSON)", "관심종목 (CSV)", "종목 메모 (CSV)", "전체 데이터 (ZIP)"],
        key='export_type'
    )

    if st.button("내보내기", type="primary", use_container_width=True, key='export_btn'):
        with st.spinner("내보내는 중..."):
            result = None

            if export_type == "포트폴리오 (CSV)":
                result = export_portfolios_to_csv()
            elif export_type == "포트폴리오 (JSON)":
                result = export_portfolios_to_json()
            elif export_type == "관심종목 (CSV)":
                result = export_watchlist_to_csv()
            elif export_type == "종목 메모 (CSV)":
                result = export_stock_notes_to_csv()
            elif export_type == "전체 데이터 (ZIP)":
                result = export_all_data_to_zip()

            if result and result['success']:
                st.success(result['message'])

                # 다운로드 버튼
                if export_type == "전체 데이터 (ZIP)":
                    st.download_button(
                        label="ZIP 파일 다운로드",
                        data=result['data'],
                        file_name=result['filename'],
                        mime="application/zip",
                        key='download_zip'
                    )
                else:
                    st.download_button(
                        label="파일 다운로드",
                        data=result['data'],
                        file_name=result['filename'],
                        mime="text/csv" if export_type.endswith("CSV)") else "application/json",
                        key='download_export'
                    )
            else:
                st.error(result['message'] if result else "내보내기 실패")


def render_data_import():
    """데이터 가져오기"""

    st.markdown("#### 데이터 가져오기")

    # 가져오기 옵션
    import_type = st.selectbox(
        "가져올 데이터 유형",
        ["포트폴리오 (CSV)", "관심종목 (CSV)", "종목 메모 (CSV)"],
        key='import_type'
    )

    # 중복 처리 옵션
    duplicate_mode = st.radio(
        "중복 데이터 처리",
        ["건너뛰기 (skip)", "교체 (replace)", "병합 (merge)"],
        key='duplicate_mode',
        horizontal=True
    )

    # 모드 값 추출
    mode_map = {
        "건너뛰기 (skip)": "skip",
        "교체 (replace)": "replace",
        "병합 (merge)": "merge"
    }
    selected_mode = mode_map[duplicate_mode]

    # 파일 업로드
    uploaded_file = st.file_uploader(
        "CSV 파일 선택",
        type=['csv'],
        key='import_upload'
    )

    if uploaded_file:
        if st.button("가져오기", type="primary", use_container_width=True, key='import_btn'):
            with st.spinner("가져오는 중..."):
                try:
                    # CSV 데이터 읽기
                    csv_data = uploaded_file.getvalue().decode('utf-8')

                    result = None

                    if import_type == "포트폴리오 (CSV)":
                        # 형식 검증
                        validation = validate_csv_format(csv_data, ['username', 'portfolio_name', 'portfolio_data'])
                        if not validation['is_valid']:
                            st.error(f"CSV 형식 오류: {validation['message']}")
                        else:
                            result = import_portfolios_from_csv(csv_data, selected_mode)

                    elif import_type == "관심종목 (CSV)":
                        validation = validate_csv_format(csv_data, ['username', 'ticker'])
                        if not validation['is_valid']:
                            st.error(f"CSV 형식 오류: {validation['message']}")
                        else:
                            result = import_watchlist_from_csv(csv_data, selected_mode)

                    elif import_type == "종목 메모 (CSV)":
                        validation = validate_csv_format(csv_data, ['username', 'ticker'])
                        if not validation['is_valid']:
                            st.error(f"CSV 형식 오류: {validation['message']}")
                        else:
                            result = import_stock_notes_from_csv(csv_data, selected_mode)

                    if result:
                        if result['success']:
                            st.success(result['message'])
                        else:
                            st.error(result['message'])

                except Exception as e:
                    st.error(f"가져오기 중 오류 발생: {str(e)}")


# ==================================================
# 사용자 관리 (기존 코드 유지)
# ==================================================

def render_user_management():
    """사용자 관리 (기존 기능)"""

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


# ==================================================
# 포트폴리오 관리 (기존 코드 유지)
# ==================================================

def render_portfolio_management():
    """전략 관리 (기존 기능)"""

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
