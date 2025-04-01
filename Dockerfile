# Use Python 3.11 on Alpine for a lightweight image
FROM python:3.11-alpine

# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev \
    openssl-dev jpeg-dev zlib-dev freetype-dev lcms2-dev \
    libwebp-dev tiff-dev tk-dev harfbuzz-dev fribidi-dev \
    ghostscript poppler-utils poppler-dev

# Upgrade pip, setuptools, and wheel before installing dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy dependencies file first (better for caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
