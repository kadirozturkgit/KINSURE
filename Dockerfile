# Container image for the KINSURE FastAPI backend.
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_DIRECTORY=/app/logs

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
