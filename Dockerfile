# Container image for the KINSURE FastAPI backend.
FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_DIRECTORY=/app/logs \
    TZ=Europe/Istanbul

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/sql ./sql

RUN mkdir -p /app/logs
RUN python -m compileall -q /app/app
RUN python -c "from app.main import app; app.openapi()"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
