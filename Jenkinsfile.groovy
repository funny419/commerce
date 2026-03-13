pipeline {
    agent any
    stages {
        stage('Environment Check') {
            steps {
                // Jenkins가 호스트의 도커를 잘 쓰는지 확인
                sh 'docker version'
            }
        }
        stage('Build') {
            steps {
                // Docker 이미지를 먼저 빌드합니다. (소스코드 및 requirements.txt가 이미지에 복사됨)
                sh 'docker build -t my-flask-app .'
            }
        }
        stage('Test') {
            steps {
                // 빌드된 이미지 내에서 테스트를 실행합니다. (volume mount 불필요)
                sh 'docker run --rm my-flask-app python tests.py'
            }
        }
        stage('Deploy') {
            steps {
                // 3. 기존 컨테이너 중지 및 새 컨테이너 실행
                sh 'docker stop flask-app || true'
                sh 'docker rm flask-app || true'
                sh 'docker run -d -p 5000:5000 --name flask-app my-flask-app'
            }
        }
    }
}