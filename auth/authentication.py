import bcrypt
import os
import re
from db.models import get_user_by_username, get_user_by_id, create_user, update_last_login, update_password


def hash_password(password):
    """비밀번호를 bcrypt로 해싱 (work factor 12)"""
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')


def verify_password(password, password_hash):
    """비밀번호 검증"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def validate_username(username):
    """사용자명 검증

    Returns:
        tuple: (is_valid, error_message)
    """
    if not username:
        return False, "사용자명을 입력하세요."

    if len(username) < 3 or len(username) > 20:
        return False, "사용자명은 3-20자여야 합니다."

    # 영문, 숫자, 언더스코어만 허용
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "사용자명은 영문, 숫자, 언더스코어만 사용할 수 있습니다."

    # 중복 체크
    existing_user = get_user_by_username(username)
    if existing_user:
        return False, "이미 사용 중인 사용자명입니다."

    return True, None


def validate_password(password):
    """비밀번호 검증

    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "비밀번호를 입력하세요."

    min_length = int(os.environ.get("MIN_PASSWORD_LENGTH", "8"))

    if len(password) < min_length:
        return False, f"비밀번호는 최소 {min_length}자 이상이어야 합니다."

    return True, None


def register_user(username, password):
    """사용자 등록

    Returns:
        tuple: (success, user_id or error_message)
    """
    # 사용자명 검증
    valid, error = validate_username(username)
    if not valid:
        return False, error

    # 비밀번호 검증
    valid, error = validate_password(password)
    if not valid:
        return False, error

    # 비밀번호 해싱 및 사용자 생성
    password_hash = hash_password(password)
    user_id = create_user(username, password_hash, is_admin=False)

    if user_id:
        return True, user_id
    else:
        return False, "사용자 등록에 실패했습니다."


def authenticate_user(username, password):
    """사용자 인증 (로그인)

    Returns:
        dict or None: 사용자 정보 또는 None
    """
    user = get_user_by_username(username)
    if not user:
        return None

    if not verify_password(password, user['password_hash']):
        return None

    # 마지막 로그인 시간 업데이트
    update_last_login(user['user_id'])

    return user


def change_password(user_id, current_password, new_password):
    """비밀번호 변경

    Args:
        user_id: 사용자 ID
        current_password: 현재 비밀번호
        new_password: 새 비밀번호

    Returns:
        tuple: (success, error_message)
    """
    # 사용자 조회
    user = get_user_by_id(user_id)
    if not user:
        return False, "사용자를 찾을 수 없습니다."

    # 현재 비밀번호 확인
    if not verify_password(current_password, user['password_hash']):
        return False, "현재 비밀번호가 일치하지 않습니다."

    # 새 비밀번호 검증
    valid, error = validate_password(new_password)
    if not valid:
        return False, error

    # 현재 비밀번호와 새 비밀번호가 같은지 확인
    if current_password == new_password:
        return False, "새 비밀번호는 현재 비밀번호와 달라야 합니다."

    # 새 비밀번호 해싱 및 업데이트
    new_password_hash = hash_password(new_password)
    if update_password(user_id, new_password_hash):
        return True, "비밀번호가 성공적으로 변경되었습니다."
    else:
        return False, "비밀번호 변경에 실패했습니다."
