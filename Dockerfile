# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=7860

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY class_names.json .
COPY best_chilli_disease_model.h5 .

# Copy templates and static files
COPY templates/ templates/
COPY static/ static/

# Create uploads directory
RUN mkdir -p uploads

# Expose port (Hugging Face uses 7860)
EXPOSE 7860

# Run with gunicorn in production
CMD gunicorn --bind 0.0.0.0:7860 --workers 2 --threads 2 --timeout 120 app:app
