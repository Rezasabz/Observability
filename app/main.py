# app/main.py
import time, random
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, SpanKind
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor




tracer = trace.get_tracer("fastapi-app", "1.0.0")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown: exporterها خودشون flush می‌کنند (env/auto-instrumentation)

app = FastAPI(title="FastAPI + OTLP via Collector", lifespan=lifespan)

# Auto-instrumentation برای FastAPI
# FastAPIInstrumentor.instrument_app(app)

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
logger.info("fastapi starting up…")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/work")
def work(q: int = 5):
    logger.info("work called q=%s", q)
    # یک span دستی کنار auto-instrumentation برای تست
    with tracer.start_as_current_span("simulate-work", kind=SpanKind.INTERNAL) as span:
        delay = random.uniform(0.05, 0.25) * q
        time.sleep(delay)
        span.set_attribute("work.q", q)
        span.set_attribute("work.delay_sec", round(delay, 3))
        if delay > 0.9:
            span.set_status(Status(StatusCode.ERROR, "too slow"))
    return {"status": "done", "delay_sec": round(delay, 3)}
