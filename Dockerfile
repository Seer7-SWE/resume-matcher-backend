FROM python:3.11-alpine  # Faster and lightweight

WORKDIR /app

COPY requirements.txt /app/

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
