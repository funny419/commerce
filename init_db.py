# /init_db.py
# 이 스크립트는 배포 시 데이터베이스 테이블을 안전하게 생성하기 위해 사용됩니다.
from app import app, db
import time
from sqlalchemy.exc import OperationalError

# DB 컨테이너가 완전히 시작될 때까지 몇 번 재시도합니다.
# docker-compose up 직후 DB 컨테이너가 요청을 받을 준비가 안됐을 수 있습니다.
retries = 5
delay = 5
for i in range(retries):
    try:
        # 애플리케이션 컨텍스트 내에서 DB 테이블 생성
        with app.app_context():
            print(f"Attempting to connect to the database (attempt {i+1}/{retries})...")
            db.create_all()
        print("✅ Database tables created successfully (or already exist).")
        break  # 성공 시 루프 종료
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        if i < retries - 1:
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            print("❌ Could not connect to the database after several retries. Aborting.")
            exit(1)  # 실패 시 비정상 종료로 워크플로우를 중단시킴