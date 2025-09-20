# # app/main.py
# import time, random
# from fastapi import FastAPI
# from contextlib import asynccontextmanager
# import logging

# from opentelemetry import trace
# from opentelemetry.trace import Status, StatusCode, SpanKind
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor




# tracer = trace.get_tracer("fastapi-app", "1.0.0")

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # startup
#     yield
#     # shutdown: exporterها خودشون flush می‌کنند (env/auto-instrumentation)

# app = FastAPI(title="FastAPI + OTLP via Collector", lifespan=lifespan)

# # Auto-instrumentation برای FastAPI
# # FastAPIInstrumentor.instrument_app(app)

# logger = logging.getLogger("app")
# logger.setLevel(logging.INFO)
# logger.info("fastapi starting up…")

# @app.get("/health")
# def health():
#     return {"ok": True}

# @app.get("/work")
# def work(q: int = 5):
#     logger.info("work called q=%s", q)
#     # یک span دستی کنار auto-instrumentation برای تست
#     with tracer.start_as_current_span("simulate-work", kind=SpanKind.INTERNAL) as span:
#         delay = random.uniform(0.05, 0.25) * q
#         time.sleep(delay)
#         span.set_attribute("work.q", q)
#         span.set_attribute("work.delay_sec", round(delay, 3))
#         if delay > 0.9:
#             span.set_status(Status(StatusCode.ERROR, "too slow"))
#     return {"status": "done", "delay_sec": round(delay, 3)}

# import os
# import time
# import random
# from fastapi import FastAPI
# from contextlib import asynccontextmanager
# import logging
# from opentelemetry.sdk.resources import Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry import trace
# from opentelemetry.trace import SpanKind, Status, StatusCode


# # مقداردهی به نام سرویس و نسخه سرویس
# otel_service_name = os.getenv("OTEL_SERVICE_NAME", "fastapi-app")
# otel_service_version = os.getenv("OTEL_SERVICE_VERSION", "1.0.0")
# otel_otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")  # آدرس OTLP exporter

# # ایجاد یک منبع برای OpenTelemetry
# resource = Resource(attributes={
#     "service.name": otel_service_name,
#     "service.version": otel_service_version,
# })

# # پیکربندی TracerProvider با استفاده از منبع (Resource) جدید
# trace.set_tracer_provider(TracerProvider(resource=resource))

# # تنظیمات OTLP exporter
# otlp_exporter = OTLPSpanExporter(endpoint=otel_otlp_endpoint, insecure=True)
# span_processor = BatchSpanProcessor(otlp_exporter)
# trace.get_tracer_provider().add_span_processor(span_processor)

# # تعریف ترکر
# tracer = trace.get_tracer(otel_service_name)

# # تنظیمات logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger("app")
# logger.setLevel(logging.INFO)
# logger.info("fastapi starting up…")

# # تعریف lifespan برای FastAPI
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # startup
#     yield
#     # shutdown: exporterها خودشون flush می‌کنند (env/auto-instrumentation)

# # اپلیکیشن FastAPI
# app = FastAPI(title="FastAPI + OTLP via Collector", lifespan=lifespan)

# @app.get("/health")
# def health():
#     return {"ok": True}

# @app.get("/work")
# def work(q: int = 5):
#     logger.info("work called q=%s", q)
#     # ایجاد یک span دستی
#     with tracer.start_as_current_span("simulate-work", kind=SpanKind.INTERNAL) as span:
#         delay = random.uniform(0.05, 0.25) * q
#         time.sleep(delay)
#         span.set_attribute("work.q", q)
#         span.set_attribute("work.delay_sec", round(delay, 3))
#         if delay > 0.9:
#             span.set_status(Status(StatusCode.ERROR, "too slow"))
#     return {"status": "done", "delay_sec": round(delay, 3)}


import os
import time
import random
from fastapi import FastAPI, Response
from contextlib import asynccontextmanager
import logging
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry import trace, metrics
from opentelemetry.trace import SpanKind, Status, StatusCode

# اضافه کردن imports برای Prometheus
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram

# مقداردهی به نام سرویس و نسخه سرویس
otel_service_name = os.getenv("OTEL_SERVICE_NAME", "fastapi-app")
otel_service_version = os.getenv("OTEL_SERVICE_VERSION", "1.0.0")
otel_otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

# ایجاد یک منبع برای OpenTelemetry
resource = Resource(attributes={
    "service.name": otel_service_name,
    "service.version": otel_service_version,
})

# پیکربندی TracerProvider
trace.set_tracer_provider(TracerProvider(resource=resource))

# پیکربندی MeterProvider برای متریک‌ها
metric_exporter = OTLPMetricExporter(endpoint=otel_otlp_endpoint, insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=5000)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

# تنظیمات OTLP exporter برای trace
otlp_exporter = OTLPSpanExporter(endpoint=otel_otlp_endpoint, insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# تعریف ترکر و متر
tracer = trace.get_tracer(otel_service_name)
meter = metrics.get_meter(otel_service_name)

# ایجاد متریک‌های OpenTelemetry
request_counter = meter.create_counter(
    "http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)

response_time_histogram = meter.create_histogram(
    "http_response_time_seconds",
    description="HTTP response time in seconds",
    unit="s"
)

# ایجاد متریک‌های Prometheus
prom_request_counter = Counter(
    'prom_http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status_code']
)

prom_response_time = Histogram(
    'prom_http_response_time_seconds',
    'HTTP response time in seconds',
    ['method', 'endpoint']
)

# تنظیمات logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# تعریف lifespan برای FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("FastAPI app starting up with metrics support...")
    yield
    # shutdown
    logger.info("FastAPI app shutting down...")

# اپلیکیشن FastAPI
app = FastAPI(title="FastAPI + OTLP via Collector + Metrics", lifespan=lifespan)

# Middleware برای ثبت متریک‌ها
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # ثبت متریک OpenTelemetry
    request_counter.add(1, {
        "method": request.method,
        "endpoint": request.url.path,
        "status_code": str(response.status_code)
    })
    
    response_time_histogram.record(process_time, {
        "method": request.method,
        "endpoint": request.url.path
    })
    
    # ثبت متریک Prometheus
    prom_request_counter.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=str(response.status_code)
    ).inc()
    
    prom_response_time.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/work")
def work(q: int = 5):
    logger.info("work called q=%s", q)
    # ایجاد یک span دستی
    with tracer.start_as_current_span("simulate-work", kind=SpanKind.INTERNAL) as span:
        delay = random.uniform(0.05, 0.25) * q
        time.sleep(delay)
        span.set_attribute("work.q", q)
        span.set_attribute("work.delay_sec", round(delay, 3))
        if delay > 0.9:
            span.set_status(Status(StatusCode.ERROR, "too slow"))
    return {"status": "done", "delay_sec": round(delay, 3)}

# endpoint جدید برای متریک‌های Prometheus
@app.get("/metrics")
def metrics_endpoint():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# endpoint جدید برای تست متریک‌ها
@app.get("/test")
def test_endpoint():
    logger.info("Test endpoint called")
    return {"message": "This is a test endpoint for metrics monitoring"}