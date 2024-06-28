
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
```
sudo dnf update -y
sudo dnf install -y docker
service docker start
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

aws s3 cp s3://fastapi-docker/fastapi-app.tar fastapi-app.tar
docker load -i fastapi-app.tar
docker run -d --name fastapi-container --restart unless-stopped -p 8000:8000 fastapi-app
```

## Fargate 서비스 설정 프로세스 요약

1. **Docker 이미지 빌드 및 ECR에 푸시**:
    - FastAPI 애플리케이션 Docker 이미지를 ECR에 푸시.
2. **ECS 클러스터 및 서비스 생성**:
    - Fargate 클러스터와 서비스를 생성.
    - Task 정의에서 Docker 이미지 사용.
3. **ALB 설정**:
    - ALB를 생성하여 외부에서 접근할 수 있도록 설정.
    - Target Group을 생성하고 ECS 서비스의 IP 주소를 등록.
4. **보안 그룹 설정**:
    - ALB와 ECS 서비스에 외부 접근을 허용하는 보안 그룹 설정.
5. **엔드포인트 테스트**:
    - ALB DNS 이름을 사용하여 FastAPI 엔드포인트에 접근.

## 1. ECR (Elastic Container Registry)에서 Docker 이미지 푸시

### a. ECR 리포지토리 생성

AWS Management Console에서 ECR을 선택하고 새 리포지토리를 생성합니다.

1. **ECR** > **Create repository** 선택
2. 리포지토리 이름 지정 (예: `fastapi-app`)
3. **Create repository** 클릭
4. [`495693425233.dkr.ecr.ap-northeast-2.amazonaws.com/fastapi-app`](http://495693425233.dkr.ecr.ap-northeast-2.amazonaws.com/fastapi-app)

### b. ECR 인증 및 Docker 이미지 푸시

AWS CLI를 사용하여 ECR에 인증하고 이미지를 푸시합니다.

```bash
# ECR 로그인
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<your-region>.amazonaws.com

aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 495693425233.dkr.ecr.ap-northeast-2.amazonaws.com

# Docker 이미지 태그 지정
docker tag fastapi-app:latest <account-id>.dkr.ecr.<your-region>.amazonaws.com/fastapi-app:latest

docker tag fastapi-app:latest 495693425233.dkr.ecr.ap-northeast-2.amazonaws.com/fastapi-app:latest

# Docker 이미지 푸시
docker push <account-id>.dkr.ecr.<your-region>.amazonaws.com/fastapi-app:latest

docker push 495693425233.dkr.ecr.ap-northeast-2.amazonaws.com/fastapi-app:latest
```

## 2. ECS (Elastic Container Service)에서 클러스터 및 서비스 생성

### a. ECS 클러스터 생성

1. **ECS** > **Clusters** > **Create Cluster** 선택
2. 인프라 **AWS Fargate(서버리스)** 선택
3. 클러스터 이름 지정 (예: `fastapi-cluster`)
4. **Create** 클릭

### b. ECS 서비스 생성

1. **ECS** > **Task Definitions** > **Create new Task Definition** 선택
2. **Fargate** 선택
3. Task 정의 설정:
    - Task 정의 이름 지정 (예: `fastapi-task`)
    - Task Role: (기본값 유지)
    - Network Mode: `awsvpc`
    - Task Size: 적절한 CPU 및 메모리 선택 (예: 0.5 vCPU, 1GB RAM)
4. **Container** 추가:
    - Container 이름: `fastapi-container`
    - Image: `<account-id>.dkr.ecr.<your-region>.amazonaws.com/fastapi-app:latest`
    `495693425233.dkr.ecr.ap-northeast-2.amazonaws.com/fastapi-app:latest`
    - Port mappings: Container port `8000`
5. **Create** 클릭

### c. ECS 서비스 생성

1. **ECS** > **Clusters** > `fastapi-cluster` > **Create Service** 선택
2. **Launch type**: `Fargate`
3. **Task Definition**: `fastapi-task`
4. **Service name**: `fastapi-service`
5. **Number of tasks**: `1`
6. **Cluster VPC**, **Subnets**, **Security groups** 설정 (다음 단계에서 보안 그룹 설정)
7. **Load Balancer** 설정 (다음 단계에서 로드 밸런서 설정)
8. **Next step** 및 **Create service** 클릭

## 3. 로드 밸런서 생성

### a. Application Load Balancer (ALB) 생성

1. **EC2** > **Load Balancers** > **Create Load Balancer** > **Application Load Balancer** 선택
2. 로드 밸런서 이름 지정 (예: `fastapi-alb`)
3. Scheme: `internet-facing`
4. IP address type: `ipv4`
5. **Listeners**: `HTTP` 포트 `80` 설정
6. **Availability Zones**: 필요한 서브넷 선택
7. **Configure Security Settings**: 기본값 유지
8. **Configure Security Groups**: 외부 접근을 허용할 보안 그룹 선택 (아래 보안 그룹 설정 참조)
9. **Configure Routing**:
    - Target group name: `fastapi-target`
    - Protocol: `HTTP`
    - Port: `8000`
10. **Create** 클릭

## 4. API 엔드포인트 설정

### a. Target Group 생성 및 등록

1. **EC2** > **Target Groups** > **Create Target Group** 선택
2. **Target type**: `IP`
3. **Protocol**: `HTTP`
4. **Port**: `8000`
5. **Target Group name**: `fastapi-target`
6. **Register Targets**: 생성된 ECS 서비스의 IP 주소 등록

## 5. 외부 접근을 위한 보안 그룹 설정

### a. 보안 그룹 설정

1. **EC2** > **Security Groups** > **Create Security Group** 선택
2. 보안 그룹 이름 지정 (예: `fastapi-sg`)
3. **Inbound rules**:
    - HTTP (포트 80) 규칙 추가 (소스: `0.0.0.0/0`, `::/0`)
4. **Outbound rules**: 기본값 유지
5. **Create Security Group** 클릭

### b. ECS 서비스 및 ALB에 보안 그룹 적용

1. ECS 서비스 및 ALB에 `fastapi-sg` 보안 그룹을 적용합니다.

## 6. FastAPI 엔드포인트 테스트

### a. 로드 밸런서 DNS로 접근

로드 밸런서의 DNS 이름을 확인하고, FastAPI 엔드포인트를 테스트합니다.

```bash
# 예: 로드 밸런서 DNS가 `fastapi-alb-1234567890.region.elb.amazonaws.com`일 경우
curl <http://fastapi-alb-1234567890.region.elb.amazonaws.com/api/bike-stations/1001>

```

### b. 웹 브라우저에서 테스트

웹 브라우저에서 `http://<로드-밸런서-DNS>/api/bike-stations/1001`으로 접속하여 FastAPI 엔드포인트가 동작하는지 확인합니다.