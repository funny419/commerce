pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // GitHub 리포지토리에서 소스 코드를 가져옵니다.
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                // OS에 따라 명령어 자동 선택 (Linux: sh, Windows: bat)
                script {
                    if (isUnix()) {
                        sh 'pip install -r requirements.txt'
                    } else {
                        bat 'pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running Unit Tests...'
                script {
                    if (isUnix()) {
                        sh 'python tests.py'
                    } else {
                        bat 'python tests.py'
                    }
                }
            }
        }
    }
}