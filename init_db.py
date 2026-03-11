from app import app, db

# app_context 안에서 데이터베이스 작업을 수행합니다.
with app.app_context():
    # 데이터베이스 테이블을 생성합니다.
    # 만약 테이블이 이미 존재한다면, 이 코드는 아무 작업도 하지 않습니다.
    db.create_all()
    print("데이터베이스 테이블이 생성(또는 업데이트)되었습니다.")