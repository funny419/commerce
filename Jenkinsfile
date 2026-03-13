pipeline {
    agent any
    stages {
        stage('Environment Check') {
            steps {
                // Jenkins가 호스트의 도커를 잘 쓰는지 확인
                sh 'docker version'
            }
        }
        stage('Test & Build') {
            steps {
                // 1. Python 이미지 안에서 pip install과 테스트 실행
                // 별도의 설치 없이 python:3.9-slim 이미지를 즉석에서 사용합니다.
                sh '''
                docker run --rm -v $(pwd):/app -w /app python:3.9-slim sh -c "
                    pip install -r requirements.txt &&
                    echo 'Dependency install success!'
                "
                '''
                
                // 2. Flask 앱 도커 이미지 빌드
                sh 'docker build -t my-flask-app .'
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