# Dockerfile

# First stage: build stage
# 베이스 이미지
FROM python:3.11-alpine as builder

# 파이썬 애플리케이션의 성능 및 동작 방식을 조정하기 위해 사용되는 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# 작업 디렉토리 설정
WORKDIR /app

# 종속성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 애플리케이션 코드 복사
COPY . /app/

# Second stage: final stage
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the application and dependencies from the builder stage
COPY --from=builder /install /usr/local
COPY --from=builder /app /app

# Set working directory
WORKDIR /app

# CPU 코어 수 및 워커 수 계산 후 FastAPI 애플리케이션 실행
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "3", "--log-level", "debug"]
CMD ["sh", "-c", "CPU_COUNT=$(grep -c processor /proc/cpuinfo) && WORKERS=$(( CPU_COUNT * 2 )) && uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug --workers $WORKERS"]
