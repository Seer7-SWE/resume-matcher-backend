# Use Python 3.11 Alpine for a lightweight image
FROM python:3.11-alpine

# Set the working directory
WORKDIR /app

# Copy dependencies file first (better for caching)
COPY requirements.txt /app/

# Install dependencies and required system packages
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
