FROM python:3.11-slim AS builder

WORKDIR /build

#Cài đặt các công cụ cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    patchelf \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pyarmor nuitka

# Copy code
COPY main.py .
COPY secret_logic.py .
COPY utils.py .

# Bước 1: PyArmor obfuscation
RUN pyarmor gen secret_logic.py && \
    pyarmor gen utils.py

# Bước 2: Nuitka compilation
RUN nuitka --standalone --onefile main.py -o app.bin

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy binary từ builder
COPY --from=builder /build/app.bin .

# Chạy với user không có quyền root
RUN useradd -m -u 1000 appuser && \
    chown appuser:appuser /app
USER appuser

CMD ["./app.bin"]