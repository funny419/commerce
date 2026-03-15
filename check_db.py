import pymysql
import sys
import os

# 접속 정보 설정os.environ.get('DB_NAME', 'board')

print(f"[{DB_HOST}]의 데이터베이스 '{DB_NAME}'에 접속을 시도합니다...")

try:
    # 접속 시도
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        charset='utf8mb4'
    )
    print("✅ 성공: MariaDB 데이터베이스에 정상적으로 접속되었습니다!")
    connection.close()
except Exception as e:
    print(f"❌ 실패: 접속 중 오류가 발생했습니다.\n{e}")