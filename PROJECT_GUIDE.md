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
- **DevOps:** Docker, GitHub Actions

## 3. 데이터베이스 정책 (Database Policy)

### 3.1. 연결 정보
- **Docker Compose 사용 시:**
  - **웹 애플리케이션 (Flask) -> DB:** 서비스 이름 `db`와 내부 포트 `3306`을 사용합니다. (`DATABASE_URI` 환경 변수로 설정)
  - **외부(호스트 PC) -> DB:** `localhost`와 외부 포트 `4807`을 사용합니다. (예: DB 관리 툴)
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

## 8. 테스트 (Testing)
- **프레임워크:** Python 표준 라이브러리 `unittest` 사용.
- **실행 파일:** `tests.py`
- **실행 환경:** 테스트는 실제 DB에 영향을 주지 않도록 메모리 기반의 **SQLite** (`sqlite:///:memory:`)를 사용하여 독립적으로 수행됩니다.
- **실행 방법:**
  ```bash
  python tests.py
  ```

## 9. CI/CD (지속적 통합/배포)
- **도구:** GitHub Actions, Docker, Docker Compose
- **파이프라인 정의:** `.github/workflows/deploy.yml`
- **배포 대상:** Windows 10 (Self-Hosted Runner 사용)

### 9.1. 파이프라인 단계 (Workflow)
1.  **Integration (CI):** GitHub 호스팅 Linux 서버(`ubuntu-latest`)에서 실행됩니다.
    -   Python 환경 설정 및 의존성 설치 (`requirements.txt`).
    -   `tests.py`를 실행하여 단위 테스트 검증.
    -   `Dockerfile` 빌드 테스트를 통해 이미지 생성 가능 여부 확인.
2.  **Deployment (CD):** 배포 대상인 Windows 10 Self-Hosted Runner에서 실행됩니다.
    -   최신 소스 코드 체크아웃 (Checkout).
    -   GitHub Secrets 및 설정값을 기반으로 `.env` 파일 생성.
    -   `docker-compose`를 사용하여 기존 컨테이너 중단 후 최신 코드로 재빌드 및 실행.
    -   사용하지 않는 Docker 이미지 정리 (Prune).