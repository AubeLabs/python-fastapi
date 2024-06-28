
# 로컬 작업
## Docker 이미지 빌드
docker build -t fastapi-app:latest .

## 기존 배포 삭제 > 새 배포 적용
kubectl delete deployment fastapi-deployment
kubectl apply -f deployment.yaml

## 또는 새 이미지로 배포 롤링 업데이트
kubectl set image deployment/fastapi-deployment fastapi-container=fastapi-app:latest

## 롤링 업데이트 상태 확인
kubectl rollout status deployment/fastapi-deployment

## 서비스 상태 확인
kubectl get services
kubectl get pods
kubectl logs <pod-name>

# Docker 이미지 빌드 및 S3에 업로드
1. ## Docker 이미지 빌드
docker build -t fastapi-app:latest .

2. ## Docker 이미지 tar 파일로 저장
docker save -o fastapi-app.tar fastapi-app:latest

3. ## AWS CLI를 사용하여 S3에 업로드
aws s3 cp fastapi-app.tar s3://fastapi-docker/fastapi-app.tar

# EC2 인스턴스에서 Docker 이미지 다운로드 및 실행
1. ## S3에서 Docker 이미지 다운로드
aws s3 cp s3://fastapi-docker/fastapi-app.tar fastapi-app.tar

2. ## Docker 이미지 로드
docker load -i fastapi-app.tar

3. ## Docker 컨테이너 시작
docker run -d --name fastapi-container --restart unless-stopped -p 8000:8000 fastapi-app


# EC2 인스턴스 생성
sudo dnf update -y
sudo dnf install -y docker
service docker start
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

aws s3 cp s3://fastapi-docker/fastapi-app.tar fastapi-app.tar
docker load -i fastapi-app.tar
docker run -d --name fastapi-container --restart unless-stopped -p 8000:8000 fastapi-app

