"""시스템 상태 모니터링"""

import os
from datetime import datetime
from typing import Dict
from db.models import db_query
from utils.backup_manager import get_backup_stats, get_db_path


# ==================================================
# 데이터베이스 통계
# ==================================================

def get_database_stats() -> Dict[str, any]:
    """
    데이터베이스 통계 정보 반환

    Returns:
        dict: DB 크기, 테이블별 레코드 수
    """
    try:
        db_path = get_db_path()

        # DB 파일 크기
        db_size = 0
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)

        # 테이블별 레코드 수 조회
        with db_query() as conn:
            cursor = conn.cursor()

            # users 테이블
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]

            # portfolios 테이블
            cursor.execute("SELECT COUNT(*) FROM portfolios")
            portfolio_count = cursor.fetchone()[0]

            # watchlist 테이블
            cursor.execute("SELECT COUNT(*) FROM watchlist")
            watchlist_count = cursor.fetchone()[0]

            # stock_notes 테이블
            cursor.execute("SELECT COUNT(*) FROM stock_notes")
            stock_notes_count = cursor.fetchone()[0]

        return {
            'db_size': db_size,
            'db_path': db_path,
            'tables': {
                'users': user_count,
                'portfolios': portfolio_count,
                'watchlist': watchlist_count,
                'stock_notes': stock_notes_count
            },
            'total_records': user_count + portfolio_count + watchlist_count + stock_notes_count
        }

    except Exception as e:
        return {
            'db_size': 0,
            'db_path': get_db_path(),
            'tables': {
                'users': 0,
                'portfolios': 0,
                'watchlist': 0,
                'stock_notes': 0
            },
            'total_records': 0,
            'error': str(e)
        }


# ==================================================
# 사용자 통계
# ==================================================

def get_user_stats() -> Dict[str, any]:
    """
    사용자 통계 정보 반환

    Returns:
        dict: 총 사용자 수, 관리자 수, 일반 사용자 수, 최근 가입일
    """
    try:
        with db_query() as conn:
            cursor = conn.cursor()

            # 총 사용자 수
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            # 관리자 수
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
            admin_count = cursor.fetchone()[0]

            # 최근 가입자
            cursor.execute("""
                SELECT username, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT 1
            """)
            latest_user = cursor.fetchone()

            # 최근 로그인
            cursor.execute("""
                SELECT username, last_login
                FROM users
                WHERE last_login IS NOT NULL
                ORDER BY last_login DESC
                LIMIT 1
            """)
            latest_login = cursor.fetchone()

        return {
            'total_users': total_users,
            'admin_count': admin_count,
            'regular_users': total_users - admin_count,
            'latest_user': {
                'username': latest_user[0] if latest_user else None,
                'created_at': latest_user[1] if latest_user else None
            },
            'latest_login': {
                'username': latest_login[0] if latest_login else None,
                'last_login': latest_login[1] if latest_login else None
            }
        }

    except Exception as e:
        return {
            'total_users': 0,
            'admin_count': 0,
            'regular_users': 0,
            'latest_user': {'username': None, 'created_at': None},
            'latest_login': {'username': None, 'last_login': None},
            'error': str(e)
        }


# ==================================================
# 포트폴리오 통계
# ==================================================

def get_portfolio_stats() -> Dict[str, any]:
    """
    포트폴리오 통계 정보 반환

    Returns:
        dict: 총 포트폴리오 수, 사용자별 평균, 최근 수정일
    """
    try:
        with db_query() as conn:
            cursor = conn.cursor()

            # 총 포트폴리오 수
            cursor.execute("SELECT COUNT(*) FROM portfolios")
            total_portfolios = cursor.fetchone()[0]

            # 사용자별 평균 포트폴리오 수
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM portfolios
            """)
            users_with_portfolios = cursor.fetchone()[0]

            avg_portfolios_per_user = 0
            if users_with_portfolios > 0:
                avg_portfolios_per_user = total_portfolios / users_with_portfolios

            # 최근 수정된 포트폴리오
            cursor.execute("""
                SELECT p.portfolio_name, p.updated_at, u.username
                FROM portfolios p
                JOIN users u ON p.user_id = u.user_id
                ORDER BY p.updated_at DESC
                LIMIT 1
            """)
            latest_portfolio = cursor.fetchone()

        return {
            'total_portfolios': total_portfolios,
            'users_with_portfolios': users_with_portfolios,
            'avg_per_user': round(avg_portfolios_per_user, 1),
            'latest_portfolio': {
                'name': latest_portfolio[0] if latest_portfolio else None,
                'updated_at': latest_portfolio[1] if latest_portfolio else None,
                'username': latest_portfolio[2] if latest_portfolio else None
            }
        }

    except Exception as e:
        return {
            'total_portfolios': 0,
            'users_with_portfolios': 0,
            'avg_per_user': 0,
            'latest_portfolio': {'name': None, 'updated_at': None, 'username': None},
            'error': str(e)
        }


# ==================================================
# 관심종목 통계
# ==================================================

def get_watchlist_stats() -> Dict[str, any]:
    """
    관심종목 통계 정보 반환

    Returns:
        dict: 총 관심종목 수, 사용자별 평균
    """
    try:
        with db_query() as conn:
            cursor = conn.cursor()

            # 총 관심종목 수
            cursor.execute("SELECT COUNT(*) FROM watchlist")
            total_watchlist = cursor.fetchone()[0]

            # 사용자별 평균
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM watchlist")
            users_with_watchlist = cursor.fetchone()[0]

            avg_per_user = 0
            if users_with_watchlist > 0:
                avg_per_user = total_watchlist / users_with_watchlist

            # 가장 많이 추가된 종목 (상위 5개)
            cursor.execute("""
                SELECT ticker, name, COUNT(*) as count
                FROM watchlist
                GROUP BY ticker
                ORDER BY count DESC
                LIMIT 5
            """)
            popular_tickers = cursor.fetchall()

        return {
            'total_watchlist': total_watchlist,
            'users_with_watchlist': users_with_watchlist,
            'avg_per_user': round(avg_per_user, 1),
            'popular_tickers': [
                {'ticker': row[0], 'name': row[1], 'count': row[2]}
                for row in popular_tickers
            ]
        }

    except Exception as e:
        return {
            'total_watchlist': 0,
            'users_with_watchlist': 0,
            'avg_per_user': 0,
            'popular_tickers': [],
            'error': str(e)
        }


# ==================================================
# 종목 메모 통계
# ==================================================

def get_stock_notes_stats() -> Dict[str, any]:
    """
    종목 메모 통계 정보 반환

    Returns:
        dict: 총 메모 수, 사용자별 평균
    """
    try:
        with db_query() as conn:
            cursor = conn.cursor()

            # 총 메모 수
            cursor.execute("SELECT COUNT(*) FROM stock_notes")
            total_notes = cursor.fetchone()[0]

            # 사용자별 평균
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM stock_notes")
            users_with_notes = cursor.fetchone()[0]

            avg_per_user = 0
            if users_with_notes > 0:
                avg_per_user = total_notes / users_with_notes

            # 최근 작성된 메모
            cursor.execute("""
                SELECT ticker, name, updated_at
                FROM stock_notes
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            latest_note = cursor.fetchone()

        return {
            'total_notes': total_notes,
            'users_with_notes': users_with_notes,
            'avg_per_user': round(avg_per_user, 1),
            'latest_note': {
                'ticker': latest_note[0] if latest_note else None,
                'name': latest_note[1] if latest_note else None,
                'updated_at': latest_note[2] if latest_note else None
            }
        }

    except Exception as e:
        return {
            'total_notes': 0,
            'users_with_notes': 0,
            'avg_per_user': 0,
            'latest_note': {'ticker': None, 'name': None, 'updated_at': None},
            'error': str(e)
        }


# ==================================================
# 시스템 개요
# ==================================================

def get_system_overview() -> Dict[str, any]:
    """
    전체 시스템 개요 정보 반환

    Returns:
        dict: 모든 통계 정보를 포함한 시스템 개요
    """
    try:
        # 각 통계 수집
        db_stats = get_database_stats()
        user_stats = get_user_stats()
        portfolio_stats = get_portfolio_stats()
        watchlist_stats = get_watchlist_stats()
        notes_stats = get_stock_notes_stats()
        backup_stats = get_backup_stats()

        return {
            'timestamp': datetime.now().isoformat(),
            'database': db_stats,
            'users': user_stats,
            'portfolios': portfolio_stats,
            'watchlist': watchlist_stats,
            'stock_notes': notes_stats,
            'backups': backup_stats
        }

    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }


# ==================================================
# 유틸리티 함수
# ==================================================

def format_bytes(size_bytes: int) -> str:
    """
    바이트를 읽기 쉬운 형식으로 변환

    Args:
        size_bytes: 바이트 단위 크기

    Returns:
        str: 포맷된 크기 문자열
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_datetime(dt_string: str) -> str:
    """
    날짜 문자열을 읽기 쉬운 형식으로 변환

    Args:
        dt_string: ISO 형식 날짜 문자열

    Returns:
        str: 포맷된 날짜 문자열
    """
    if not dt_string:
        return "N/A"

    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_string[:16] if len(dt_string) >= 16 else dt_string
