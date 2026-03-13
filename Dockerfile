# 1. 베이스 이미지로 Python 3.9-slim 버전을 사용합니다.
FROM python:3.9-slim

# 2. 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# 3. 의존성 파일을 먼저 복사하여 pip 캐시를 활용합니다.
COPY requirements.txt .

# 4. 의존성을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 5. 나머지 소스 코드를 복사합니다.
COPY . .

# 6. Gunicorn WSGI 서버를 사용하여 애플리케이션을 실행합니다.
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]