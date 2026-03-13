# Flask Q&A 게시판 프로젝트 개발 가이드

## 1. 프로젝트 개요
**Flask** 프레임워크를 기반으로 한 질문 및 답변(Q&A) 커뮤니티 게시판입니다. 사용자는 질문을 올리고, 다른 사용자의 질문에 답변하며, 댓글과 추천 기능을 통해 상호작용할 수 있습니다.

## 2. 기술 스택 (Tech Stack)
- **Language:** Python 3.x
- **Web Framework:** Flask
- **ORM:** Flask-SQLAlchemy
- **Database:** MariaDB (초기 SQLite에서 마이그레이션)
- **Frontend:** HTML5, CSS3, JavaScript (jQuery)
- **UI Framework:** Bootstrap 4.6
- **Editor:** Summernote (WYSIWYG)

## 3. 데이터베이스 정책 (Database Policy)

### 3.1. 연결 정보
- **Host:** 192.168.2.23 (내부 윈도우 머신)
- **DB Name:** board
- **User:** funny / **Password:** strim100
- **Library:** `pymysql` 드라이버 사용 (`mysql+pymysql://...`)

### 3.2. 스키마 주요 변경 사항
- **User 테이블:**
  - `password_hash`: MariaDB의 엄격한 길이 제한을 고려하여 `VARCHAR(255)`로 설정 (초기 128자에서 확장).
- **관계 설정:**
  - `Post`와 `User` (작성자): 1:N
  - `Post`와 `User` (추천인): N:M (별도의 `post_voter` 연결 테이블 사용)
  - `Post`와 `Comment`/`Answer`: 1:N (Cascade Delete 적용)

## 4. 코딩 원칙 및 컨벤션 (Coding Principles)

### 4.1. 백엔드 (Flask)
- **라우팅:** 기능별로 명확한 URL 패턴을 사용합니다. (예: `/post/<id>/delete`, `/answer/<id>/update`)
- **권한 체크:**
  - 로그인 여부는 `g.user`를 통해 확인합니다.
  - 수정/삭제 기능 접근 시, 작성자(`author`)와 현재 사용자(`g.user`)가 일치하는지 반드시 서버 사이드에서 검증합니다.
- **보안:**
  - 비밀번호는 `werkzeug.security`를 사용하여 해시화 저장합니다.
  - HTML 컨텐츠 렌더링 시 XSS 방지를 위해 필요한 부분에만 `|safe` 필터를 사용합니다.

### 4.2. 프론트엔드 (UI/UX)
- **레이아웃:** `base.html`을 상속받아 일관된 헤더와 푸터 스타일을 유지합니다.
- **라이브러리 로딩:** jQuery와 Bootstrap JS는 `<head>` 영역에서 로드하여 Summernote 등 의존성 스크립트가 본문(`body`)에서 즉시 실행될 수 있도록 합니다.
- **사용자 피드백:**
  - `flash` 메시지를 사용하여 작업 성공/실패 여부를 사용자에게 알립니다.
  - 삭제와 같은 중요 작업 시 브라우저 기본 `confirm` 대신 **Bootstrap Modal**을 사용하여 사용자 실수를 방지합니다.

## 5. 기능 상세 명세 (Feature Specifications)

### 5.1. 게시글 (Post)
- **CRUD:** 작성, 조회, 수정, 삭제 가능.
- **에디터:** Summernote 에디터 적용 (이미지, 텍스트 서식 지원).
- **목록:** 페이징(Pagination) 처리, 최신순 정렬.
- **검색:** 제목+내용 통합 검색 기능.
- **추천:** 게시글 추천 기능 (본인 글 추천 불가).

### 5.2. 답변 (Answer)
- **구조:** 하나의 게시글에 여러 답변 작성 가능.
- **기능:** 작성, 수정, 삭제, 추천.
- **채택(Adopt):** 질문 작성자는 하나의 답변을 채택할 수 있으며, 채택된 답변은 강조 표시됩니다. (본인 답변 채택 불가)

### 5.3. 댓글 (Comment)
- **범위:** 게시글 하단에 간단한 의견을 남기는 기능.
- **에디터:** Summernote 'Lite' 버전 적용 (툴바 최소화).
- **UI:**
  - 내용이 길어질 경우(100px 이상) 자동으로 접히고 '더보기' 버튼 생성.
  - 삭제 시 전용 모달 창 팝업.

## 6. 에디터 설정 (Summernote Config)

### 6.1. 게시글/답변용 (Full Toolbar)
```javascript
$('#summernote').summernote({
    height: 400,
    lang: 'ko-KR',
    toolbar: [
        ['style', ['style']],
        ['font', ['bold', 'underline', 'clear']],
        ['color', ['color']],
        ['para', ['ul', 'ol', 'paragraph']],
        ['table', ['table']],
        ['insert', ['link', 'picture', 'video']],
        ['view', ['fullscreen', 'codeview', 'help']]
    ]
});
```

### 6.2. 댓글용 (Mini Toolbar)
```javascript
$('#comment_content').summernote({
    height: 100,
    lang: 'ko-KR',
    toolbar: [
        ['font', ['bold', 'underline', 'clear']],
        ['insert', ['link']],
        ['view', ['codeview']]
    ]
});
```

## 7. 향후 개선 사항 (To-Do)
- **파일 업로드:** 현재 에디터 이미지는 Base64로 저장되므로, 서버 파일 시스템 저장 방식으로 변경 고려.
- **답변 추천 백엔드:** UI는 구현되었으나 백엔드 라우트(`vote_answer`) 및 DB 모델(`voters`) 연결 필요.
- **보안 강화:** `bleach` 라이브러리를 도입하여 HTML 태그 화이트리스트 필터링 적용 필요.