# FROM python:3.11-slim

# ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# WORKDIR /app

# # پیش‌نیازهای سبک
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     ca-certificates curl && \
#     rm -rf /var/lib/apt/lists/*

# # نصب وابستگی‌ها
# COPY app/requirements.txt /app/requirements.txt
# RUN python -m venv /opt/venv && . /opt/venv/bin/activate && \
#     pip install --no-cache-dir -r /app/requirements.txt

# # کد برنامه
# COPY app /app/app

# EXPOSE 8000

# # اجرای اپ با auto-instrumentation (exporterها از ENV می‌آیند)

# CMD ["/bin/sh", "-c", ". /opt/venv/bin/activate && \
#   opentelemetry-instrument \
#     --traces_exporter otlp --metrics_exporter otlp --logs_exporter otlp \
#     uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info --access-log"]

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt
RUN python -m venv /opt/venv && . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

EXPOSE 8000

CMD ["/bin/sh", "-c", ". /opt/venv/bin/activate && \
  opentelemetry-instrument \
    --traces_exporter otlp \
    --metrics_exporter otlp \
    --logs_exporter otlp \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info --access-log"]
