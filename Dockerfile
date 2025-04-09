

# ---------- STAGE 1: Build ----------
    FROM python:3.11-slim AS builder

    WORKDIR /app
    COPY requirements.txt .
    
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc libffi-dev python3-dev \
        && pip install --no-cache-dir --upgrade pip setuptools wheel \
        && pip install --no-cache-dir -r requirements.txt \
        && python -m spacy download en_core_web_sm \
        && apt-get remove -y build-essential gcc libffi-dev python3-dev \
        && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
    
    COPY . .
    
    # ---------- STAGE 2: Runtime ----------
    FROM python:3.11-slim
    
    WORKDIR /app
    COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
    COPY --from=builder /usr/local/bin /usr/local/bin
    COPY --from=builder /app /app
    
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    