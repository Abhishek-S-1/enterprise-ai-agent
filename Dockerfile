# ==========================================
# Production Dockerfile for Enterprise AI Agent
# Optimized for CPU-Only (Small Size)
# ==========================================

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. Install System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. CRITICAL STEP: Install CPU-only PyTorch FIRST
# This prevents pip from downloading the massive GPU version later.
# We install torch, torchvision, and torchaudio from the CPU index.
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. Install remaining dependencies
COPY requirements.txt .
# We use --no-deps for libraries that might try to reinstall GPU torch
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir streamlit

COPY . .

# 4. Create Non-Root User
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]