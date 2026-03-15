# render_template 함수를 추가로 가져옵니다.
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
import os, datetime

app = Flask(__name__)

# --- 데이터베이스 설정 ---
# 1. 환경 변수(DATABASE_URI)에서 데이터베이스 URI를 가져옵니다.
# 2. 환경 변수가 없으면, 로컬 개발용 기본 URI를 사용합니다.
db_uri = os.environ.get('DATABASE_URI', 'mysql+pymysql://funny:strim100@mariadb:4807/board?charset=utf8mb4')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# flash 메시지, session 등 Flask의 특정 기능을 사용하려면 시크릿 키가 필요합니다.
app.config['SECRET_KEY'] = 'dev' # 개발용 키입니다. 실제 운영 환경에서는 예측 불가능한 복잡한 키를 사용해야 합니다.

db = SQLAlchemy(app)

# --- 게시물 추천인(voter) 연결 테이블 ---
post_voter = db.Table(
    'post_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), primary_key=True)
)

# --- 사용자 모델(데이터베이스 테이블) 정의 ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- 게시물 모델(데이터베이스 테이블) 정의 ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # user.id를 외래 키로 설정하여 User 모델과 연결합니다.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Post 모델에서 작성자 정보에 접근할 수 있도록 관계를 설정합니다. (예: post.author)
    author = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
    # Post 모델에서 댓글 정보에 접근할 수 있도록 관계를 설정합니다.
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    # Post 모델에서 답변 정보에 접근할 수 있도록 관계를 설정합니다.
    answers = db.relationship('Answer', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    # Post 모델에서 추천인 정보에 접근할 수 있도록 관계를 설정합니다.
    voters = db.relationship('User', secondary=post_voter, backref=db.backref('voted_posts', lazy='dynamic'))
    # 조회수 필드 추가
    view_count = db.Column(db.Integer, default=0, nullable=False)

# --- 댓글 모델(데이터베이스 테이블) 정의 ---
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))

# --- 답변 모델(데이터베이스 테이블) 정의 ---
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('answers', lazy='dynamic'))
    is_adopted = db.Column(db.Boolean, default=False, nullable=False)

@app.before_request
def load_logged_in_user():
    """요청이 처리되기 전에, 세션에 사용자 ID가 있으면 사용자 정보를 로드합니다."""
    user_id = session.get('user_id')
    g.user = User.query.get(user_id) if user_id is not None else None

@app.route('/')
def index():
    title_text = "초간단 게시판"
    # 페이지 번호를 가져옵니다. 기본값은 1입니다.
    page = request.args.get('page', type=int, default=1)
    # 검색어를 가져옵니다.
    keyword = request.args.get('keyword', type=str, default='')

    query = Post.query
    if keyword:
        search = f'%{keyword}%'
        query = query.filter(or_(Post.title.like(search), Post.content.like(search)))

    # 최신순으로 정렬하여 페이지네이션 객체를 생성합니다. (페이지당 5개 게시물)
    posts = query.order_by(Post.id.desc()).paginate(page=page, per_page=5, error_out=False)
    return render_template('index.html', board_title=title_text, posts=posts, keyword=keyword)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user: # 이미 로그인된 사용자는 메인 페이지로 보냅니다.
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # 사용자 이름 또는 이메일이 이미 존재하는지 확인
        if User.query.filter_by(username=username).first():
            flash('이미 사용 중인 사용자 이름입니다.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger')
            return redirect(url_for('register'))

        # 새 사용자 생성 및 비밀번호 설정
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('회원가입이 완료되었습니다! 로그인해주세요.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user: # 이미 로그인된 사용자는 메인 페이지로 보냅니다.
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('사용자 이름 또는 비밀번호가 올바르지 않습니다.', 'danger')
            return redirect(url_for('login'))

        # 세션을 초기화하고, 새로운 사용자 ID를 저장하여 로그인 상태로 만듭니다.
        session.clear()
        session['user_id'] = user.id
        flash(f'환영합니다, {user.username}님!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/post/create', methods=['GET', 'POST'])
def create_post():
    # 로그인하지 않은 사용자는 로그인 페이지로 보냅니다.
    if not g.user:
        flash('글을 작성하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # 새 게시물 객체를 생성하고, 작성자를 현재 로그인된 사용자로 설정합니다.
        new_post = Post(title=title, content=content, author=g.user)
        db.session.add(new_post)
        db.session.commit()

        flash('게시물이 성공적으로 작성되었습니다.', 'success')
        return redirect(url_for('index'))

    return render_template('create_post.html')

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    # post_id에 해당하는 게시물을 데이터베이스에서 찾고, 없으면 404 오류를 표시합니다.
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        if not g.user:
            flash('댓글을 작성하려면 로그인이 필요합니다.', 'warning')
            return redirect(url_for('login'))
        
        content = request.form.get('content')
        if not content or not content.strip():
            flash('댓글 내용이 없습니다.', 'danger')
        else:
            comment = Comment(content=content, author=g.user, post=post)
            db.session.add(comment)
            db.session.commit()
            flash('댓글이 작성되었습니다.', 'success')
        return redirect(url_for('post_detail', post_id=post_id))

    # 이 코드는 POST 요청 시에는 실행되지 않고, GET 요청 시에만 실행됩니다.
    # 조회수를 1 증가시킵니다.
    # (post.view_count or 0)은 혹시 모를 null 값에 대비한 안전장치입니다.
    post.view_count = (post.view_count or 0) + 1
    db.session.commit()

    comments = post.comments.order_by(Comment.timestamp.asc()).all()
    answers = post.answers.order_by(Answer.timestamp.asc()).all()
    return render_template('post_detail.html', post=post, comments=comments, answers=answers)

@app.route('/post/<int:post_id>/vote', methods=['POST'])
def vote_post(post_id):
    if not g.user:
        flash('추천하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)

    if post.author == g.user:
        flash('자신이 작성한 글은 추천할 수 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))

    if g.user in post.voters:
        post.voters.remove(g.user)
        flash('추천을 취소했습니다.', 'info')
    else:
        post.voters.append(g.user)
        flash('게시물을 추천했습니다.', 'success')
    db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/post/<int:post_id>/answer/create', methods=['POST'])
def create_answer(post_id):
    if not g.user:
        flash('답변을 작성하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('login'))
    
    post = Post.query.get_or_404(post_id)
    title = request.form['title']
    content = request.form['content']
    
    answer = Answer(title=title, content=content, author=g.user, post=post)
    db.session.add(answer)
    db.session.commit()
    
    flash('답변이 등록되었습니다.', 'success')
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/answer/<int:answer_id>/update', methods=['GET', 'POST'])
def update_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)

    if g.user != answer.author:
        flash('수정 권한이 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=answer.post_id))

    if request.method == 'POST':
        answer.title = request.form['title']
        answer.content = request.form['content']
        db.session.commit()
        flash('답변이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('post_detail', post_id=answer.post_id))

    return render_template('update_answer.html', answer=answer)

@app.route('/answer/<int:answer_id>/delete', methods=['POST'])
def delete_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    post_id = answer.post_id
    if g.user != answer.author:
        flash('삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))
    
    db.session.delete(answer)
    db.session.commit()
    flash('답변이 삭제되었습니다.', 'success')
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/answer/<int:answer_id>/adopt', methods=['POST'])
def adopt_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    post = answer.post

    # 게시물 작성자만 채택 가능
    if g.user != post.author:
        flash('답변을 채택할 권한이 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=post.id))

    # 게시물 작성자가 자신의 답변을 채택할 수 없음
    if post.author == answer.author:
        flash('자신이 작성한 답변은 채택할 수 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=post.id))

    # 기존에 채택된 답변이 있다면 해제
    for other_answer in post.answers:
        other_answer.is_adopted = False
    
    # 현재 답변을 채택
    answer.is_adopted = True
    db.session.commit()
    
    flash('답변을 채택했습니다.', 'success')
    return redirect(url_for('post_detail', post_id=post.id))

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    # 현재 로그인한 사용자가 게시물 작성자가 아니면, 권한이 없음을 알리고 상세 페이지로 돌려보냅니다.
    if g.user != post.author:
        flash('수정 권한이 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('게시물이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('update_post.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if g.user != post.author:
        flash('삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))
    
    db.session.delete(post)
    db.session.commit()
    flash('게시물이 삭제되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/comment/<int:comment_id>/update', methods=['GET', 'POST'])
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if g.user != comment.author:
        flash('수정 권한이 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=comment.post_id))

    if request.method == 'POST':
        new_content = request.form.get('content')
        if not new_content or not new_content.strip():
            flash('댓글 내용이 없습니다.', 'danger')
        else:
            comment.content = new_content
            db.session.commit()
            flash('댓글이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('post_detail', post_id=comment.post_id))

    return render_template('update_comment.html', comment=comment)

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id # 리디렉션을 위해 post_id를 미리 저장합니다.
    if g.user != comment.author:
        flash('삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))
    
    db.session.delete(comment)
    db.session.commit()
    flash('댓글이 삭제되었습니다.', 'success')
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/logout')
def logout():
    session.clear() # 세션을 비워서 로그아웃 처리합니다.
    flash('성공적으로 로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/user/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # 사용자가 작성한 게시물과 답변을 최신순으로 가져옵니다.
    user_posts = user.posts.order_by(Post.id.desc()).all()
    user_answers = user.answers.order_by(Answer.timestamp.desc()).all()
    return render_template('user_profile.html', user=user, posts=user_posts, answers=user_answers)


@app.route('/user/edit', methods=['GET', 'POST'])
def edit_profile():
    if not g.user:
        flash('프로필을 수정하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        
        if not g.user.check_password(password):
            flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('edit_profile'))

        changes_made = False
        if email != g.user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != g.user.id:
                flash('이미 사용 중인 이메일입니다.', 'danger')
                return redirect(url_for('edit_profile'))
            g.user.email = email
            changes_made = True

        if new_password:
            if new_password != confirm_new_password:
                flash('새 비밀번호가 일치하지 않습니다.', 'danger')
                return redirect(url_for('edit_profile'))
            g.user.set_password(new_password)
            changes_made = True
        
        if changes_made:
            db.session.commit()
            flash('프로필이 성공적으로 업데이트되었습니다.', 'success')
        
        return redirect(url_for('user_profile', username=g.user.username))

    return render_template('edit_profile.html')
