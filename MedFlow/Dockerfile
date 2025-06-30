# MedFlow: AI-Powered Patient Intake Assistant
# Docker configuration for containerized deployment

# Use Python 3.10 Bullseye as base image
FROM python:3.10-bullseye

# Create application directory structure
RUN mkdir /app
RUN mkdir /app/assets
RUN mkdir /app/utils

# Copy application files
COPY *.py /app/
COPY requirements.txt /app/
COPY assets/* /app/assets/
COPY utils/* /app/utils/

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose the application port
EXPOSE 7860

# Start the MedFlow patient intake server
CMD ["python3", "server.py"]