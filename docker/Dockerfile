FROM python:3.11-slim

WORKDIR /app

# Copy code
COPY main.py .
COPY secret_logic.py .
COPY utils.py .

CMD ["python", "main.py"]