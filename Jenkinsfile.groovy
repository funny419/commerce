pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // GitHub 리포지토리에서 소스 코드를 가져옵니다.
                checkout scm
            }
        }

        stage('Test') {
            steps {
                echo 'Running Unit Tests in a container...'
                // Python 컨테이너를 임시로 실행하여 의존성 설치 및 테스트를 수행합니다.
                sh '''
                docker run --rm -v $(pwd):/app -w /app python:3.9-slim sh -c "
                    pip install -r requirements.txt &&
                    python tests.py
                "
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker image...'
                // Dockerfile을 사용하여 Flask 애플리케이션 이미지를 빌드합니다.
                sh 'docker build -t my-flask-app:latest .'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                // 기존 컨테이너를 중지/제거하고 새 버전의 컨테이너를 실행합니다.
                // -e 옵션으로 데이터베이스 접속 정보를 환경 변수로 전달합니다.
                sh 'docker stop flask-app || true && docker rm flask-app || true'
                sh 'docker run -d -p 5000:5000 --name flask-app -e DATABASE_URI="mysql+pymysql://funny:strim100@192.168.1.23/board?charset=utf8mb4" my-flask-app:latest'
            }
        }
    }
}