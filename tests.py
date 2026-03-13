import unittest
from app import app, db, User, Post, Answer

class BoardTestCase(unittest.TestCase):
    def setUp(self):
        """
        테스트 시작 전 실행:
        실제 DB(MariaDB) 대신 테스트용 인메모리 SQLite DB를 설정합니다.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # 테스트 편의를 위해 CSRF 비활성화 (폼 검증 시)
        
        self.client = app.test_client()
        
        # 애플리케이션 컨텍스트 안에서 DB 생성
        with app.app_context():
            db.create_all()
            self.create_test_user()

    def tearDown(self):
        """테스트 종료 후 실행: DB 정리"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_user(self):
        """테스트용 사용자 생성 헬퍼 함수"""
        user = User(username='tester', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        
        user2 = User(username='other', email='other@example.com')
        user2.set_password('password123')
        db.session.add(user2)
        
        db.session.commit()

    def login(self, username, password):
        """로그인 헬퍼 함수"""
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """로그아웃 헬퍼 함수"""
        return self.client.get('/logout', follow_redirects=True)

    # --- 테스트 케이스 시작 ---

    def test_main_page(self):
        """메인 페이지 접속 테스트"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Flask Board', response.data)

    def test_login_logout(self):
        """로그인 및 로그아웃 기능 테스트"""
        # 로그인 성공
        rv = self.login('tester', 'password123')
        self.assertIn(b'tester', rv.data)  # 로그인 후 상단에 닉네임 표시 확인
        
        # 로그인 실패 (비밀번호 오류)
        rv = self.login('tester', 'wrongpass')
        self.assertIn(b'danger', rv.data) # 에러 메시지(Flash) 클래스 확인

        # 로그아웃
        rv = self.logout()
        self.assertIn(b'success', rv.data)

    def test_create_post(self):
        """게시글 작성 테스트"""
        self.login('tester', 'password123')
        rv = self.client.post('/post/create', data=dict(
            title='테스트 게시글',
            content='테스트 내용입니다.'
        ), follow_redirects=True)
        
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'\xed\x85\x8c\x8a\xa4\xed\x8a\xb8 \xea\xb2\x8c\xec\x8b\x9c\xea\xb8\x80', rv.data) # '테스트 게시글' (UTF-8 bytes)

    def test_post_permission(self):
        """게시글 수정/삭제 권한 테스트"""
        # 1. tester가 글 작성
        self.login('tester', 'password123')
        self.client.post('/post/create', data=dict(title='내글', content='내용'), follow_redirects=True)
        
        # 작성된 글 ID 확인
        with app.app_context():
            post = Post.query.filter_by(title='내글').first()
            post_id = post.id

        self.logout()

        # 2. other 사용자로 로그인하여 수정 시도
        self.login('other', 'password123')
        rv = self.client.post(f'/post/{post_id}/update', data=dict(
            title='해킹시도', content='수정됨'
        ), follow_redirects=True)
        
        # 권한 없음 메시지 확인
        self.assertIn(b'danger', rv.data)
        
        # 데이터가 변경되지 않았는지 확인
        with app.app_context():
            post = Post.query.get(post_id)
            self.assertEqual(post.title, '내글')

    def test_create_answer(self):
        """답변 작성 테스트"""
        # 글 작성
        self.login('tester', 'password123')
        self.client.post('/post/create', data=dict(title='질문', content='질문내용'), follow_redirects=True)
        
        with app.app_context():
            post = Post.query.first()
            post_id = post.id

        # 답변 작성
        rv = self.client.post(f'/post/{post_id}/answer/create', data=dict(
            title='답변', content='답변내용'
        ), follow_redirects=True)
        
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'\xeb\x8b\xb5\xeb\xb3\x80\xeb\x82\xb4\xec\x9a\xa9', rv.data) # '답변내용' 확인

if __name__ == '__main__':
    unittest.main()