#!/usr/bin/env python3
"""
my_portfolios.json 데이터를 SQLite 데이터베이스로 마이그레이션하는 스크립트

실행 방법:
    python -m utils.migration
"""

import os
import json
import sys
import shutil
from pathlib import Path
from getpass import getpass

# 프로젝트 루트 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from db.database import init_database
from db.models import get_user_by_username, save_portfolio
from auth.authentication import register_user


def migrate_json_to_db():
    """JSON 파일의 포트폴리오를 데이터베이스로 마이그레이션"""

    print("=" * 60)
    print("Portfolio Data Migration Script")
    print("=" * 60)
    print()

    # 환경변수 로드
    load_dotenv()

    # JSON 파일 경로
    json_file = "my_portfolios.json"

    if not os.path.exists(json_file):
        print(f"[ERROR] '{json_file}' 파일을 찾을 수 없습니다.")
        print("마이그레이션할 데이터가 없습니다.")
        return

    # JSON 파일 읽기
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            portfolios = json.load(f)
    except Exception as e:
        print(f"[ERROR] JSON 파일 읽기 실패: {e}")
        return

    if not portfolios:
        print("JSON 파일에 포트폴리오가 없습니다.")
        return

    print(f"'{json_file}'에서 {len(portfolios)}개의 포트폴리오를 발견했습니다.")
    print()

    # 사용자 계정 입력
    print("이 포트폴리오들을 어느 사용자 계정으로 이관하시겠습니까?")
    print("(새 사용자 계정을 생성하거나 기존 계정을 사용할 수 있습니다)")
    print()

    username = input("사용자명: ").strip()
    if not username:
        print("[ERROR] 사용자명을 입력하지 않았습니다.")
        return

    # 데이터베이스 초기화
    init_database()

    # 기존 사용자 확인
    existing_user = get_user_by_username(username)

    if existing_user:
        print(f"[SUCCESS] 기존 사용자 '{username}' 계정을 사용합니다.")
        user_id = existing_user['user_id']
    else:
        print(f"새 사용자 '{username}' 계정을 생성합니다.")
        password = getpass("비밀번호: ")
        password_confirm = getpass("비밀번호 확인: ")

        if password != password_confirm:
            print("[ERROR] 비밀번호가 일치하지 않습니다.")
            return

        success, result = register_user(username, password)
        if not success:
            print(f"[ERROR] 사용자 생성 실패: {result}")
            return

        user_id = result
        print(f"[SUCCESS] 사용자 '{username}' 계정이 생성되었습니다.")

    print()
    print(f"{len(portfolios)}개의 포트폴리오를 데이터베이스로 마이그레이션 중...")
    print()

    # 포트폴리오 마이그레이션
    success_count = 0
    fail_count = 0

    for portfolio_name, portfolio_data in portfolios.items():
        try:
            save_portfolio(user_id, portfolio_name, json.dumps(portfolio_data))
            print(f"  [SUCCESS] '{portfolio_name}' 마이그레이션 완료")
            success_count += 1
        except Exception as e:
            print(f"  [ERROR] '{portfolio_name}' 마이그레이션 실패: {e}")
            fail_count += 1

    print()
    print("=" * 60)
    print(f"마이그레이션 완료: {success_count}개 성공, {fail_count}개 실패")
    print("=" * 60)
    print()

    # JSON 파일 백업
    backup_file = f"{json_file}.backup"
    try:
        shutil.copy(json_file, backup_file)
        print(f"원본 JSON 파일이 '{backup_file}'로 백업되었습니다.")
        print(f"   원본 파일 '{json_file}'은 그대로 유지됩니다.")
    except Exception as e:
        print(f"[WARNING] 백업 실패: {e}")

    print()
    print("마이그레이션이 완료되었습니다!")
    print("   이제 애플리케이션을 실행하여 로그인 후 포트폴리오를 확인하세요.")


if __name__ == "__main__":
    try:
        migrate_json_to_db()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] 마이그레이션이 취소되었습니다.")
    except Exception as e:
        print(f"\n\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
