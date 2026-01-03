"""데이터베이스 백업 및 복원 관리"""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


# ==================================================
# 설정
# ==================================================

def get_db_path():
    """데이터베이스 파일 경로 반환"""
    return os.environ.get("DATABASE_PATH", "./data/portfolios.db")


def get_backup_dir():
    """백업 디렉토리 경로 반환"""
    return os.environ.get("BACKUP_DIR", "./backups")


def ensure_backup_dir():
    """백업 디렉토리 생성 (없으면)"""
    backup_dir = get_backup_dir()
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir


# ==================================================
# 백업 생성
# ==================================================

def create_backup(description: str = "") -> Dict[str, any]:
    """
    데이터베이스 백업 생성

    Args:
        description: 백업 설명 (선택)

    Returns:
        dict: 백업 정보 (success, backup_file, message)
    """
    try:
        db_path = get_db_path()

        # DB 파일 존재 확인
        if not os.path.exists(db_path):
            return {
                'success': False,
                'backup_file': None,
                'message': f"데이터베이스 파일을 찾을 수 없습니다: {db_path}"
            }

        # 백업 디렉토리 생성
        backup_dir = ensure_backup_dir()

        # 백업 파일명 생성 (타임스탬프)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"portfolios_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        # 디스크 공간 확인 (DB 크기의 2배 이상 필요)
        db_size = os.path.getsize(db_path)
        stat = os.statvfs(backup_dir)
        free_space = stat.f_bavail * stat.f_frsize

        if free_space < db_size * 2:
            return {
                'success': False,
                'backup_file': None,
                'message': f"디스크 공간이 부족합니다. (필요: {db_size * 2 / 1024:.1f} KB, 사용 가능: {free_space / 1024:.1f} KB)"
            }

        # SQLite 백업 (안전한 방법)
        # 파일 복사 대신 SQLite의 backup API 사용 (트랜잭션 안전)
        source_conn = sqlite3.connect(db_path)
        backup_conn = sqlite3.connect(backup_path)

        with backup_conn:
            source_conn.backup(backup_conn)

        source_conn.close()
        backup_conn.close()

        # 백업 파일 검증
        validation_result = validate_backup(backup_path)
        if not validation_result['is_valid']:
            # 검증 실패 시 백업 파일 삭제
            if os.path.exists(backup_path):
                os.remove(backup_path)
            return {
                'success': False,
                'backup_file': None,
                'message': f"백업 검증 실패: {validation_result['message']}"
            }

        # 백업 파일 크기 계산
        backup_size = os.path.getsize(backup_path)

        return {
            'success': True,
            'backup_file': backup_filename,
            'backup_path': backup_path,
            'size': backup_size,
            'message': f"백업이 성공적으로 생성되었습니다. ({backup_size / 1024:.1f} KB)"
        }

    except Exception as e:
        return {
            'success': False,
            'backup_file': None,
            'message': f"백업 생성 중 오류 발생: {str(e)}"
        }


# ==================================================
# 백업 목록 조회
# ==================================================

def list_backups() -> List[Dict[str, any]]:
    """
    백업 파일 목록 조회

    Returns:
        list: 백업 파일 정보 목록 (파일명, 날짜, 크기 등)
    """
    try:
        backup_dir = get_backup_dir()

        if not os.path.exists(backup_dir):
            return []

        backups = []

        # .db 파일만 필터링
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db') and filename.startswith('portfolios_'):
                filepath = os.path.join(backup_dir, filename)

                # 파일 정보 수집
                file_stat = os.stat(filepath)

                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': file_stat.st_size,
                    'created_at': datetime.fromtimestamp(file_stat.st_mtime),
                    'created_timestamp': file_stat.st_mtime
                })

        # 최신순 정렬
        backups.sort(key=lambda x: x['created_timestamp'], reverse=True)

        return backups

    except Exception as e:
        print(f"백업 목록 조회 중 오류: {str(e)}")
        return []


# ==================================================
# 백업 복원
# ==================================================

def restore_backup(backup_filename: str, create_safety_backup: bool = True) -> Dict[str, any]:
    """
    백업 파일로부터 데이터베이스 복원

    Args:
        backup_filename: 복원할 백업 파일명
        create_safety_backup: 복원 전 안전 백업 생성 여부 (기본값: True)

    Returns:
        dict: 복원 결과 (success, message, safety_backup)
    """
    try:
        db_path = get_db_path()
        backup_dir = get_backup_dir()
        backup_path = os.path.join(backup_dir, backup_filename)

        # 백업 파일 존재 확인
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'message': f"백업 파일을 찾을 수 없습니다: {backup_filename}"
            }

        # 백업 파일 검증
        validation_result = validate_backup(backup_path)
        if not validation_result['is_valid']:
            return {
                'success': False,
                'message': f"백업 파일 검증 실패: {validation_result['message']}"
            }

        # 안전 백업 생성 (복원 전 현재 DB 백업)
        safety_backup_info = None
        if create_safety_backup and os.path.exists(db_path):
            safety_result = create_backup(description="복원 전 자동 백업")
            if safety_result['success']:
                safety_backup_info = safety_result['backup_file']
            else:
                return {
                    'success': False,
                    'message': f"안전 백업 생성 실패: {safety_result['message']}"
                }

        # 데이터베이스 복원 (파일 교체)
        try:
            # 기존 DB 파일 백업 (임시)
            temp_db_path = db_path + ".temp"
            if os.path.exists(db_path):
                shutil.copy2(db_path, temp_db_path)

            # 백업 파일로 복원
            shutil.copy2(backup_path, db_path)

            # 복원된 DB 검증
            validation_result = validate_backup(db_path)
            if not validation_result['is_valid']:
                # 검증 실패 시 롤백
                if os.path.exists(temp_db_path):
                    shutil.copy2(temp_db_path, db_path)
                raise Exception(f"복원된 DB 검증 실패: {validation_result['message']}")

            # 임시 파일 삭제
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)

            return {
                'success': True,
                'message': f"데이터베이스가 성공적으로 복원되었습니다.",
                'safety_backup': safety_backup_info
            }

        except Exception as e:
            # 복원 실패 시 롤백
            if os.path.exists(temp_db_path):
                shutil.copy2(temp_db_path, db_path)
                os.remove(temp_db_path)
            raise e

    except Exception as e:
        return {
            'success': False,
            'message': f"복원 중 오류 발생: {str(e)}"
        }


# ==================================================
# 백업 삭제
# ==================================================

def delete_backup(backup_filename: str) -> Dict[str, any]:
    """
    백업 파일 삭제

    Args:
        backup_filename: 삭제할 백업 파일명

    Returns:
        dict: 삭제 결과 (success, message)
    """
    try:
        backup_dir = get_backup_dir()
        backup_path = os.path.join(backup_dir, backup_filename)

        # 파일 존재 확인
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'message': f"백업 파일을 찾을 수 없습니다: {backup_filename}"
            }

        # 파일 삭제
        os.remove(backup_path)

        return {
            'success': True,
            'message': f"백업 파일이 삭제되었습니다: {backup_filename}"
        }

    except Exception as e:
        return {
            'success': False,
            'message': f"삭제 중 오류 발생: {str(e)}"
        }


# ==================================================
# 백업 검증
# ==================================================

def validate_backup(backup_path: str) -> Dict[str, any]:
    """
    백업 파일 무결성 검증

    Args:
        backup_path: 검증할 백업 파일 경로

    Returns:
        dict: 검증 결과 (is_valid, message)
    """
    try:
        # 파일 존재 확인
        if not os.path.exists(backup_path):
            return {
                'is_valid': False,
                'message': "파일이 존재하지 않습니다."
            }

        # 파일 크기 확인 (최소 1KB)
        if os.path.getsize(backup_path) < 1024:
            return {
                'is_valid': False,
                'message': "파일 크기가 너무 작습니다. (손상된 파일일 수 있음)"
            }

        # SQLite integrity check
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()

        conn.close()

        if result and result[0] == 'ok':
            return {
                'is_valid': True,
                'message': "백업 파일이 정상입니다."
            }
        else:
            return {
                'is_valid': False,
                'message': f"SQLite 무결성 검사 실패: {result[0] if result else 'Unknown'}"
            }

    except sqlite3.DatabaseError as e:
        return {
            'is_valid': False,
            'message': f"SQLite 오류: {str(e)}"
        }
    except Exception as e:
        return {
            'is_valid': False,
            'message': f"검증 중 오류 발생: {str(e)}"
        }


# ==================================================
# 백업 파일 업로드 및 저장
# ==================================================

def save_uploaded_backup(uploaded_file, filename: str = None) -> Dict[str, any]:
    """
    업로드된 백업 파일 저장

    Args:
        uploaded_file: Streamlit UploadedFile 객체
        filename: 저장할 파일명 (None이면 타임스탬프 생성)

    Returns:
        dict: 저장 결과 (success, filename, message)
    """
    try:
        backup_dir = ensure_backup_dir()

        # 파일명 생성
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portfolios_uploaded_{timestamp}.db"

        # 파일명 검증 (.db 확장자 강제)
        if not filename.endswith('.db'):
            filename += '.db'

        backup_path = os.path.join(backup_dir, filename)

        # 파일 저장
        with open(backup_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # 저장된 파일 검증
        validation_result = validate_backup(backup_path)
        if not validation_result['is_valid']:
            # 검증 실패 시 파일 삭제
            if os.path.exists(backup_path):
                os.remove(backup_path)
            return {
                'success': False,
                'filename': None,
                'message': f"업로드된 파일 검증 실패: {validation_result['message']}"
            }

        return {
            'success': True,
            'filename': filename,
            'filepath': backup_path,
            'message': f"백업 파일이 업로드되었습니다: {filename}"
        }

    except Exception as e:
        return {
            'success': False,
            'filename': None,
            'message': f"파일 업로드 중 오류 발생: {str(e)}"
        }


# ==================================================
# 유틸리티 함수
# ==================================================

def get_backup_stats() -> Dict[str, any]:
    """
    백업 통계 정보 반환

    Returns:
        dict: 백업 통계 (총 개수, 총 크기, 가장 최근 백업 날짜)
    """
    backups = list_backups()

    if not backups:
        return {
            'count': 0,
            'total_size': 0,
            'latest_backup': None
        }

    total_size = sum(b['size'] for b in backups)
    latest_backup = backups[0]['created_at'] if backups else None

    return {
        'count': len(backups),
        'total_size': total_size,
        'latest_backup': latest_backup
    }


def format_file_size(size_bytes: int) -> str:
    """
    파일 크기를 읽기 쉬운 형식으로 변환

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
