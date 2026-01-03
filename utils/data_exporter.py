"""데이터 내보내기 및 가져오기"""

import json
import csv
import io
import zipfile
from datetime import datetime
from typing import Dict, List, Optional
from db.models import (
    db_query, db_transaction,
    get_all_users, get_all_portfolios,
    save_portfolio, add_to_watchlist, save_stock_note
)


# ==================================================
# 데이터 내보내기
# ==================================================

def export_portfolios_to_json() -> Dict[str, any]:
    """
    모든 포트폴리오를 JSON 형식으로 내보내기

    Returns:
        dict: 내보내기 결과 (success, data, message)
    """
    try:
        portfolios = get_all_portfolios()

        # 포트폴리오 데이터 구조화
        export_data = []
        for portfolio in portfolios:
            export_data.append({
                'username': portfolio['username'],
                'portfolio_name': portfolio['portfolio_name'],
                'portfolio_data': portfolio.get('portfolio_data', ''),
                'created_at': portfolio.get('created_at', ''),
                'updated_at': portfolio.get('updated_at', '')
            })

        # JSON 문자열 생성
        json_string = json.dumps(export_data, ensure_ascii=False, indent=2)

        return {
            'success': True,
            'data': json_string,
            'filename': f"portfolios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            'count': len(export_data),
            'message': f"{len(export_data)}개의 포트폴리오를 내보냈습니다."
        }

    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f"내보내기 중 오류 발생: {str(e)}"
        }


def export_portfolios_to_csv() -> Dict[str, any]:
    """
    모든 포트폴리오를 CSV 형식으로 내보내기

    Returns:
        dict: 내보내기 결과 (success, data, message)
    """
    try:
        with db_query() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.username, p.portfolio_name, p.portfolio_data,
                       p.created_at, p.updated_at
                FROM portfolios p
                JOIN users u ON p.user_id = u.user_id
                ORDER BY u.username, p.portfolio_name
            """)
            rows = cursor.fetchall()

        # CSV 문자열 생성
        output = io.StringIO()
        writer = csv.writer(output)

        # 헤더 작성
        writer.writerow(['username', 'portfolio_name', 'portfolio_data', 'created_at', 'updated_at'])

        # 데이터 작성
        for row in rows:
            writer.writerow(row)

        csv_string = output.getvalue()
        output.close()

        return {
            'success': True,
            'data': csv_string,
            'filename': f"portfolios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            'count': len(rows),
            'message': f"{len(rows)}개의 포트폴리오를 내보냈습니다."
        }

    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f"내보내기 중 오류 발생: {str(e)}"
        }


def export_watchlist_to_csv() -> Dict[str, any]:
    """
    모든 관심종목을 CSV 형식으로 내보내기

    Returns:
        dict: 내보내기 결과 (success, data, message)
    """
    try:
        with db_query() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.username, w.ticker, w.name, w.currency, w.created_at
                FROM watchlist w
                JOIN users u ON w.user_id = u.user_id
                ORDER BY u.username, w.ticker
            """)
            rows = cursor.fetchall()

        # CSV 문자열 생성
        output = io.StringIO()
        writer = csv.writer(output)

        # 헤더 작성
        writer.writerow(['username', 'ticker', 'name', 'currency', 'created_at'])

        # 데이터 작성
        for row in rows:
            writer.writerow(row)

        csv_string = output.getvalue()
        output.close()

        return {
            'success': True,
            'data': csv_string,
            'filename': f"watchlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            'count': len(rows),
            'message': f"{len(rows)}개의 관심종목을 내보냈습니다."
        }

    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f"내보내기 중 오류 발생: {str(e)}"
        }


def export_stock_notes_to_csv() -> Dict[str, any]:
    """
    모든 종목 메모를 CSV 형식으로 내보내기

    Returns:
        dict: 내보내기 결과 (success, data, message)
    """
    try:
        with db_query() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.username, sn.ticker, sn.name, sn.note_content,
                       sn.created_at, sn.updated_at
                FROM stock_notes sn
                JOIN users u ON sn.user_id = u.user_id
                ORDER BY u.username, sn.ticker
            """)
            rows = cursor.fetchall()

        # CSV 문자열 생성
        output = io.StringIO()
        writer = csv.writer(output)

        # 헤더 작성
        writer.writerow(['username', 'ticker', 'name', 'note_content', 'created_at', 'updated_at'])

        # 데이터 작성
        for row in rows:
            writer.writerow(row)

        csv_string = output.getvalue()
        output.close()

        return {
            'success': True,
            'data': csv_string,
            'filename': f"stock_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            'count': len(rows),
            'message': f"{len(rows)}개의 종목 메모를 내보냈습니다."
        }

    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f"내보내기 중 오류 발생: {str(e)}"
        }


def export_all_data_to_zip() -> Dict[str, any]:
    """
    모든 데이터를 ZIP 파일로 내보내기

    Returns:
        dict: 내보내기 결과 (success, data, message)
    """
    try:
        # 각 테이블 데이터 내보내기
        portfolios_csv = export_portfolios_to_csv()
        watchlist_csv = export_watchlist_to_csv()
        notes_csv = export_stock_notes_to_csv()

        # ZIP 파일 생성
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 포트폴리오
            if portfolios_csv['success']:
                zip_file.writestr(portfolios_csv['filename'], portfolios_csv['data'])

            # 관심종목
            if watchlist_csv['success']:
                zip_file.writestr(watchlist_csv['filename'], watchlist_csv['data'])

            # 종목 메모
            if notes_csv['success']:
                zip_file.writestr(notes_csv['filename'], notes_csv['data'])

            # 메타데이터 추가
            metadata = {
                'export_date': datetime.now().isoformat(),
                'portfolios_count': portfolios_csv.get('count', 0),
                'watchlist_count': watchlist_csv.get('count', 0),
                'notes_count': notes_csv.get('count', 0)
            }
            zip_file.writestr('metadata.json', json.dumps(metadata, ensure_ascii=False, indent=2))

        zip_data = zip_buffer.getvalue()
        zip_buffer.close()

        return {
            'success': True,
            'data': zip_data,
            'filename': f"invest_lab_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            'message': "모든 데이터를 ZIP 파일로 내보냈습니다."
        }

    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f"내보내기 중 오류 발생: {str(e)}"
        }


# ==================================================
# 데이터 가져오기
# ==================================================

def import_portfolios_from_csv(csv_data: str, duplicate_mode: str = 'skip') -> Dict[str, any]:
    """
    CSV 데이터로부터 포트폴리오 가져오기

    Args:
        csv_data: CSV 문자열
        duplicate_mode: 중복 처리 방식 ('skip', 'replace', 'merge')

    Returns:
        dict: 가져오기 결과 (success, imported_count, skipped_count, message)
    """
    try:
        # CSV 파싱
        csv_file = io.StringIO(csv_data)
        reader = csv.DictReader(csv_file)

        imported_count = 0
        skipped_count = 0
        error_count = 0

        # 사용자명 -> user_id 매핑
        username_to_id = {}
        with db_query() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username FROM users")
            for row in cursor.fetchall():
                username_to_id[row[1]] = row[0]

        # 각 행 처리
        for row in reader:
            username = row.get('username', '').strip()
            portfolio_name = row.get('portfolio_name', '').strip()
            portfolio_data = row.get('portfolio_data', '').strip()

            # 유효성 검사
            if not username or not portfolio_name or not portfolio_data:
                skipped_count += 1
                continue

            # 사용자 ID 찾기
            user_id = username_to_id.get(username)
            if not user_id:
                skipped_count += 1
                continue

            # 중복 확인
            with db_query() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT portfolio_id FROM portfolios
                    WHERE user_id = ? AND portfolio_name = ?
                """, (user_id, portfolio_name))
                existing = cursor.fetchone()

            # 중복 처리
            if existing:
                if duplicate_mode == 'skip':
                    skipped_count += 1
                    continue
                elif duplicate_mode == 'replace':
                    # 기존 포트폴리오 업데이트
                    try:
                        save_portfolio(user_id, portfolio_name, portfolio_data)
                        imported_count += 1
                    except:
                        error_count += 1
                else:  # merge는 replace와 동일하게 처리
                    try:
                        save_portfolio(user_id, portfolio_name, portfolio_data)
                        imported_count += 1
                    except:
                        error_count += 1
            else:
                # 새 포트폴리오 생성
                try:
                    save_portfolio(user_id, portfolio_name, portfolio_data)
                    imported_count += 1
                except:
                    error_count += 1

        csv_file.close()

        return {
            'success': True,
            'imported_count': imported_count,
            'skipped_count': skipped_count,
            'error_count': error_count,
            'message': f"{imported_count}개 가져오기 완료, {skipped_count}개 건너뜀, {error_count}개 오류"
        }

    except Exception as e:
        return {
            'success': False,
            'imported_count': 0,
            'skipped_count': 0,
            'error_count': 0,
            'message': f"가져오기 중 오류 발생: {str(e)}"
        }


def import_watchlist_from_csv(csv_data: str, duplicate_mode: str = 'skip') -> Dict[str, any]:
    """
    CSV 데이터로부터 관심종목 가져오기

    Args:
        csv_data: CSV 문자열
        duplicate_mode: 중복 처리 방식 ('skip', 'replace')

    Returns:
        dict: 가져오기 결과 (success, imported_count, skipped_count, message)
    """
    try:
        # CSV 파싱
        csv_file = io.StringIO(csv_data)
        reader = csv.DictReader(csv_file)

        imported_count = 0
        skipped_count = 0
        error_count = 0

        # 사용자명 -> user_id 매핑
        username_to_id = {}
        with db_query() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username FROM users")
            for row in cursor.fetchall():
                username_to_id[row[1]] = row[0]

        # 각 행 처리
        for row in reader:
            username = row.get('username', '').strip()
            ticker = row.get('ticker', '').strip()
            name = row.get('name', '').strip()
            currency = row.get('currency', 'USD').strip()

            # 유효성 검사
            if not username or not ticker:
                skipped_count += 1
                continue

            # 사용자 ID 찾기
            user_id = username_to_id.get(username)
            if not user_id:
                skipped_count += 1
                continue

            # 중복 확인
            with db_query() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT watchlist_id FROM watchlist
                    WHERE user_id = ? AND ticker = ?
                """, (user_id, ticker))
                existing = cursor.fetchone()

            # 중복 처리
            if existing:
                if duplicate_mode == 'skip':
                    skipped_count += 1
                    continue
                # replace는 skip과 동일 (watchlist는 업데이트 기능 없음)
                else:
                    skipped_count += 1
                    continue
            else:
                # 새 관심종목 추가
                try:
                    add_to_watchlist(user_id, ticker, name, currency)
                    imported_count += 1
                except:
                    error_count += 1

        csv_file.close()

        return {
            'success': True,
            'imported_count': imported_count,
            'skipped_count': skipped_count,
            'error_count': error_count,
            'message': f"{imported_count}개 가져오기 완료, {skipped_count}개 건너뜀, {error_count}개 오류"
        }

    except Exception as e:
        return {
            'success': False,
            'imported_count': 0,
            'skipped_count': 0,
            'error_count': 0,
            'message': f"가져오기 중 오류 발생: {str(e)}"
        }


def import_stock_notes_from_csv(csv_data: str, duplicate_mode: str = 'skip') -> Dict[str, any]:
    """
    CSV 데이터로부터 종목 메모 가져오기

    Args:
        csv_data: CSV 문자열
        duplicate_mode: 중복 처리 방식 ('skip', 'replace', 'merge')

    Returns:
        dict: 가져오기 결과 (success, imported_count, skipped_count, message)
    """
    try:
        # CSV 파싱
        csv_file = io.StringIO(csv_data)
        reader = csv.DictReader(csv_file)

        imported_count = 0
        skipped_count = 0
        error_count = 0

        # 사용자명 -> user_id 매핑
        username_to_id = {}
        with db_query() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username FROM users")
            for row in cursor.fetchall():
                username_to_id[row[1]] = row[0]

        # 각 행 처리
        for row in reader:
            username = row.get('username', '').strip()
            ticker = row.get('ticker', '').strip()
            name = row.get('name', '').strip()
            note_content = row.get('note_content', '').strip()

            # 유효성 검사
            if not username or not ticker:
                skipped_count += 1
                continue

            # 사용자 ID 찾기
            user_id = username_to_id.get(username)
            if not user_id:
                skipped_count += 1
                continue

            # 중복 확인
            with db_query() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT note_id, note_content FROM stock_notes
                    WHERE user_id = ? AND ticker = ?
                """, (user_id, ticker))
                existing = cursor.fetchone()

            # 중복 처리
            if existing:
                if duplicate_mode == 'skip':
                    skipped_count += 1
                    continue
                elif duplicate_mode == 'replace':
                    # 기존 메모 교체
                    try:
                        save_stock_note(user_id, ticker, name, note_content)
                        imported_count += 1
                    except:
                        error_count += 1
                else:  # merge
                    # 기존 메모에 새 내용 추가
                    try:
                        existing_content = existing[1] if existing[1] else ''
                        merged_content = f"{existing_content}\n\n--- 가져온 내용 ---\n{note_content}"
                        save_stock_note(user_id, ticker, name, merged_content)
                        imported_count += 1
                    except:
                        error_count += 1
            else:
                # 새 메모 생성
                try:
                    save_stock_note(user_id, ticker, name, note_content)
                    imported_count += 1
                except:
                    error_count += 1

        csv_file.close()

        return {
            'success': True,
            'imported_count': imported_count,
            'skipped_count': skipped_count,
            'error_count': error_count,
            'message': f"{imported_count}개 가져오기 완료, {skipped_count}개 건너뜀, {error_count}개 오류"
        }

    except Exception as e:
        return {
            'success': False,
            'imported_count': 0,
            'skipped_count': 0,
            'error_count': 0,
            'message': f"가져오기 중 오류 발생: {str(e)}"
        }


# ==================================================
# 유틸리티 함수
# ==================================================

def validate_csv_format(csv_data: str, expected_headers: List[str]) -> Dict[str, any]:
    """
    CSV 형식 유효성 검사

    Args:
        csv_data: CSV 문자열
        expected_headers: 예상되는 헤더 리스트

    Returns:
        dict: 검증 결과 (is_valid, message)
    """
    try:
        csv_file = io.StringIO(csv_data)
        reader = csv.DictReader(csv_file)

        # 헤더 확인
        headers = reader.fieldnames
        csv_file.close()

        if not headers:
            return {
                'is_valid': False,
                'message': "CSV 파일에 헤더가 없습니다."
            }

        missing_headers = set(expected_headers) - set(headers)
        if missing_headers:
            return {
                'is_valid': False,
                'message': f"누락된 헤더: {', '.join(missing_headers)}"
            }

        return {
            'is_valid': True,
            'message': "CSV 형식이 올바릅니다."
        }

    except Exception as e:
        return {
            'is_valid': False,
            'message': f"CSV 형식 오류: {str(e)}"
        }
