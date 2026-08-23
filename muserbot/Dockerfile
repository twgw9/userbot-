# syntax=docker/dockerfile:1
FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies & OpenSSL / Git
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    libffi-dev \
    libssl-dev \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Web Dashboard port
EXPOSE 8000

# Default entrypoint
CMD ["python3", "reuserbot/main.py"]
