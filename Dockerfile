# ==========================================
# Production Dockerfile for Enterprise AI Agent
# Optimized for LangChain, FAISS, and DSPy
# ==========================================

# 1. Base Image: Use slim for smaller footprint and better security
FROM python:3.10-slim

# 2. Set Environment Variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk
# PYTHONUNBUFFERED: Ensures logs are streamed directly to cloud logging (CloudWatch)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Install System Dependencies
# libgomp1: Required for FAISS and PyTorch optimizations
# build-essential: For compiling any necessary C extensions
# curl: For healthchecks
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Set Working Directory
WORKDIR /app

# 5. Install Python Dependencies
# Copy requirements first to leverage Docker layer caching. 
# If you change app.py but not requirements, this step is skipped (faster builds).
COPY requirements.txt .

# Upgrade pip and install dependencies
# --no-cache-dir: Reduces image size by not storing the pip cache
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit  # Explicitly adding streamlit as it was missing in the list

# 6. Copy Application Code
COPY . .

# 7. Security: Run as Non-Root User
# Create a user 'appuser' so the container doesn't run with root privileges
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# 8. Expose Port
# Streamlit runs on 8501 by default
EXPOSE 8501

# 9. Healthcheck (Production Best Practice)
# AWS Load Balancers use this to verify the container is alive
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 10. Entrypoint
# Runs the Streamlit app on container start
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]