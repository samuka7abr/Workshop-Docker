# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim

RUN useradd --create-home --shell /bin/bash app
WORKDIR /app

COPY --from=builder /install /usr/local
COPY app.py .

USER app

EXPOSE 5000

CMD ["python", "app.py"]
