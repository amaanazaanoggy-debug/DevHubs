FROM python:3.11-slim

WORKDIR /app

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose standard web port
EXPOSE 5000

# Default command for production container
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "run:app"]
