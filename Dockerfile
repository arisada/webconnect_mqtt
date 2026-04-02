# Use lightweight Python base
FROM python:alpine

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure stdout/stderr are unbuffered (important for logs in Docker)
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Install system dependencies only if needed
# (remove this section if your requirements are pure Python)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY porsche_web_mqtt.py .
# Default command
CMD ["python", "porsche_web_mqtt.py"]
