# Stage 1: build
FROM python:3.13.7-slim AS build
WORKDIR /app

# Install system dependencies required for building C extensions
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir cython pyarmor pyinstaller
RUN python setup.py build_ext --inplace
RUN pyarmor generate --output /app/dist_obf main.py
RUN pyinstaller --onefile /app/dist_obf/main.py -n myapp

# Stage 2: final runtime
FROM python:3.13.7-slim AS runtime
WORKDIR /app
COPY --from=build /app/dist/myapp /app/myapp
CMD ["./myapp"]
