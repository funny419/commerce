@echo off
echo [INFO] Start Deployment...

:: 1. 최신 소스 코드 가져오기 (Git이 설치되어 있어야 합니다)
echo [INFO] Pulling latest code from Git...
git pull

:: 2. 기존 컨테이너 내리기 (데이터 볼륨은 삭제되지 않음)
echo [INFO] Stopping current containers...
docker-compose down

:: 3. 이미지를 새로 빌드하고 컨테이너 실행 (Detached mode)
echo [INFO] Building and Starting containers...
docker-compose up -d --build

:: 4. 불필요한 이미지(dangling images) 정리
echo [INFO] Cleaning up unused images...
docker image prune -f

echo [SUCCESS] Deployment Completed!
pause