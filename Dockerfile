# Use slim Python for smaller images
FROM python:3.12-slim

# Make logs unbuffered & avoid .pyc files
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# Workdir inside the container
WORKDIR /app

# System build deps for some wheels
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app
