# MedFlow: AI-Powered Patient Intake Assistant
# Docker configuration for containerized deployment

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
EXPOSE 7860

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the MedFlow application
CMD ["python", "medflow.py"]