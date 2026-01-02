"""데이터베이스 모델 및 쿼리 함수"""

import sqlite3
from contextlib import contextmanager
from db.database import get_db_connection


@contextmanager
def db_transaction():
    """데이터베이스 트랜잭션 컨텍스트 매니저"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def db_query():
    """데이터베이스 조회용 컨텍스트 매니저"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


# ==================================================
# User 관련 함수
# ==================================================

def create_user(username, password_hash, is_admin=False):
    """새 사용자 생성"""
    try:
        with db_transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (?, ?, ?)
            """, (username, password_hash, 1 if is_admin else 0))
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None


def get_user(identifier, by='username'):
    """
    사용자 조회

    Args:
        identifier: 조회할 값 (username 또는 user_id)
        by: 조회 기준 ('username' 또는 'id')

    Returns:
        dict or None: 사용자 정보
    """
    column = 'username' if by == 'username' else 'user_id'

    with db_query() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT user_id, username, password_hash, is_admin, created_at, last_login
            FROM users
            WHERE {column} = ?
        """, (identifier,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_username(username):
    """사용자명으로 사용자 조회"""
    return get_user(username, by='username')


def get_user_by_id(user_id):
    """사용자 ID로 사용자 조회"""
    return get_user(user_id, by='id')


def delete_user(user_id):
    """사용자 삭제 (관련 포트폴리오도 cascade 삭제)"""
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        return cursor.rowcount > 0


def get_all_users():
    """모든 사용자 조회 (관리자용)"""
    with db_query() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username, is_admin, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def update_last_login(user_id):
    """마지막 로그인 시간 업데이트"""
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))
        return cursor.rowcount > 0


def update_password(user_id, new_password_hash):
    """사용자 비밀번호 업데이트"""
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET password_hash = ?
            WHERE user_id = ?
        """, (new_password_hash, user_id))
        return cursor.rowcount > 0


# ==================================================
# Portfolio 관련 함수
# ==================================================

def save_portfolio(user_id, portfolio_name, portfolio_data):
    """포트폴리오 저장 (없으면 INSERT, 있으면 UPDATE)"""
    with db_transaction() as conn:
        cursor = conn.cursor()

        # 기존 포트폴리오 확인
        cursor.execute("""
            SELECT portfolio_id FROM portfolios
            WHERE user_id = ? AND portfolio_name = ?
        """, (user_id, portfolio_name))

        existing = cursor.fetchone()

        if existing:
            # UPDATE
            cursor.execute("""
                UPDATE portfolios
                SET portfolio_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND portfolio_name = ?
            """, (portfolio_data, user_id, portfolio_name))
            return existing['portfolio_id']
        else:
            # INSERT
            cursor.execute("""
                INSERT INTO portfolios (user_id, portfolio_name, portfolio_data)
                VALUES (?, ?, ?)
            """, (user_id, portfolio_name, portfolio_data))
            return cursor.lastrowid


def get_user_portfolios(user_id):
    """사용자의 모든 포트폴리오 조회"""
    with db_query() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT portfolio_id, portfolio_name, portfolio_data, created_at, updated_at
            FROM portfolios
            WHERE user_id = ?
            ORDER BY updated_at DESC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_portfolio(user_id, portfolio_name):
    """특정 포트폴리오 조회"""
    with db_query() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT portfolio_id, portfolio_name, portfolio_data, created_at, updated_at
            FROM portfolios
            WHERE user_id = ? AND portfolio_name = ?
        """, (user_id, portfolio_name))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_portfolio(user_id=None, portfolio_name=None, portfolio_id=None):
    """
    포트폴리오 삭제

    Args:
        user_id: 사용자 ID (portfolio_name과 함께 사용)
        portfolio_name: 포트폴리오 이름
        portfolio_id: 포트폴리오 ID (단독 사용 가능)

    Returns:
        bool: 삭제 성공 여부
    """
    with db_transaction() as conn:
        cursor = conn.cursor()

        if portfolio_id is not None:
            cursor.execute("DELETE FROM portfolios WHERE portfolio_id = ?", (portfolio_id,))
        elif user_id is not None and portfolio_name is not None:
            cursor.execute("""
                DELETE FROM portfolios
                WHERE user_id = ? AND portfolio_name = ?
            """, (user_id, portfolio_name))
        else:
            return False

        return cursor.rowcount > 0


def delete_portfolio_by_id(portfolio_id):
    """포트폴리오 ID로 삭제 (관리자용) - 호환성을 위해 유지"""
    return delete_portfolio(portfolio_id=portfolio_id)


def get_all_portfolios():
    """모든 포트폴리오 조회 (관리자용)"""
    with db_query() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.portfolio_id, p.portfolio_name, p.created_at, p.updated_at,
                   u.username
            FROM portfolios p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY p.updated_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


# ==================================================
# Watchlist 관련 함수
# ==================================================

def add_to_watchlist(user_id, ticker, name=None, currency='USD'):
    """관심종목 추가"""
    try:
        with db_transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO watchlist (user_id, ticker, name, currency)
                VALUES (?, ?, ?, ?)
            """, (user_id, ticker, name, currency))
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        # 이미 존재하는 경우
        return None


def remove_from_watchlist(user_id, ticker):
    """관심종목 삭제"""
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM watchlist
            WHERE user_id = ? AND ticker = ?
        """, (user_id, ticker))
        return cursor.rowcount > 0


def get_user_watchlist(user_id):
    """사용자의 관심종목 목록 조회"""
    with db_query() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT watchlist_id, ticker, name, currency, created_at
            FROM watchlist
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def is_in_watchlist(user_id, ticker):
    """관심종목 여부 확인"""
    with db_query() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM watchlist
            WHERE user_id = ? AND ticker = ?
        """, (user_id, ticker))
        return cursor.fetchone() is not None


# ==================================================
# Stock Notes 관련 함수
# ==================================================

def save_stock_note(user_id, ticker, name=None, note_content=None):
    """
    종목 메모 저장 (없으면 INSERT, 있으면 UPDATE)

    Args:
        user_id: 사용자 ID
        ticker: 종목 티커
        name: 종목명 (선택)
        note_content: 메모 내용

    Returns:
        int: note_id
    """
    with db_transaction() as conn:
        cursor = conn.cursor()

        # 기존 메모 확인
        cursor.execute("""
            SELECT note_id FROM stock_notes
            WHERE user_id = ? AND ticker = ?
        """, (user_id, ticker))

        existing = cursor.fetchone()

        if existing:
            # UPDATE
            cursor.execute("""
                UPDATE stock_notes
                SET note_content = ?, name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND ticker = ?
            """, (note_content, name, user_id, ticker))
            return existing['note_id']
        else:
            # INSERT
            cursor.execute("""
                INSERT INTO stock_notes (user_id, ticker, name, note_content)
                VALUES (?, ?, ?, ?)
            """, (user_id, ticker, name, note_content))
            return cursor.lastrowid


def get_stock_note(user_id, ticker):
    """
    특정 종목의 메모 조회

    Args:
        user_id: 사용자 ID
        ticker: 종목 티커

    Returns:
        dict or None: 메모 정보 (note_id, ticker, name, note_content, created_at, updated_at)
    """
    with db_query() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT note_id, ticker, name, note_content, created_at, updated_at
            FROM stock_notes
            WHERE user_id = ? AND ticker = ?
        """, (user_id, ticker))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_stock_note(user_id, ticker):
    """
    종목 메모 삭제

    Args:
        user_id: 사용자 ID
        ticker: 종목 티커

    Returns:
        bool: 삭제 성공 여부
    """
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM stock_notes
            WHERE user_id = ? AND ticker = ?
        """, (user_id, ticker))
        return cursor.rowcount > 0


def get_user_stock_notes(user_id):
    """
    사용자의 모든 종목 메모 조회

    Args:
        user_id: 사용자 ID

    Returns:
        list: 메모 목록
    """
    with db_query() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT note_id, ticker, name, note_content, created_at, updated_at
            FROM stock_notes
            WHERE user_id = ?
            ORDER BY updated_at DESC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
