import sqlite3
import os
from pathlib import Path


def get_db_connection():
    """SQLite 데이터베이스 연결 반환"""
    db_path = os.environ.get("DATABASE_PATH", "./data/portfolios.db")

    # 데이터베이스 디렉토리 생성
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # dict처럼 접근 가능

    # Foreign key 제약조건 활성화
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_database():
    """데이터베이스 테이블 및 인덱스 생성"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # users 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)

    # portfolios 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            portfolio_name TEXT NOT NULL,
            portfolio_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, portfolio_name)
        )
    """)

    # watchlist 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            watchlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            name TEXT,
            currency TEXT DEFAULT 'USD',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, ticker)
        )
    """)

    # stock_notes 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_notes (
            note_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            name TEXT,
            note_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, ticker)
        )
    """)

    # 인덱스 생성
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON watchlist(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_stock_notes_user_id ON stock_notes(user_id)
    """)

    conn.commit()
    conn.close()

    # 관리자 계정 생성
    create_admin_user()


def create_admin_user():
    """환경변수에서 관리자 계정 생성 (첫 실행 시)"""
    from auth.authentication import hash_password
    from db.models import get_user_by_username, create_user

    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin")

    # 관리자 계정이 이미 존재하는지 확인
    existing_admin = get_user_by_username(admin_username)
    if existing_admin:
        return

    # 관리자 계정 생성
    password_hash = hash_password(admin_password)
    create_user(admin_username, password_hash, is_admin=True)
