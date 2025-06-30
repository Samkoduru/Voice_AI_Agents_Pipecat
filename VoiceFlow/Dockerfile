# VoiceFlow AI Assistant Docker Configuration
# Multi-stage build for optimized production deployment

# Use Python 3.10 Bullseye as base image
FROM python:3.10-bullseye

# Set working directory in container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the application port
EXPOSE 8765

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the VoiceFlow application
CMD ["python", "voiceflow.py"]
