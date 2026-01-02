#!/bin/bash

# 데이터베이스 백업 스크립트
# 사용법: ./backup.sh

set -e

# 설정
BACKUP_DIR="./backups"
DB_PATH="./data/portfolios.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/portfolios_$DATE.db"

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

# 데이터베이스 파일 존재 확인
if [ ! -f "$DB_PATH" ]; then
    echo "[ERROR] 데이터베이스 파일을 찾을 수 없습니다: $DB_PATH"
    exit 1
fi

# 백업 실행
echo "[INFO] 데이터베이스 백업 시작..."
cp "$DB_PATH" "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "[SUCCESS] 백업 성공: $BACKUP_FILE"

    # 백업 파일 크기 확인
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[INFO] 백업 파일 크기: $SIZE"
else
    echo "[ERROR] 백업 실패"
    exit 1
fi

# 30일 이상 된 백업 파일 삭제
echo "[INFO] 오래된 백업 파일 정리 중..."
DELETED=$(find "$BACKUP_DIR" -name "portfolios_*.db" -mtime +30 -delete -print | wc -l)
if [ "$DELETED" -gt 0 ]; then
    echo "[INFO] $DELETED 개의 오래된 백업 파일 삭제됨"
else
    echo "[INFO] 삭제할 오래된 백업 파일 없음"
fi

# 백업 목록 표시
echo ""
echo "현재 백업 목록:"
ls -lh "$BACKUP_DIR"/portfolios_*.db 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'

echo ""
echo "[SUCCESS] 백업 작업 완료"
