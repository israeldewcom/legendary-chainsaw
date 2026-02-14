from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time
from typing import Callable
import structlog

logger = structlog.get_logger()

# Define metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

active_users = Gauge("active_users", "Number of active users")
transactions_processed = Counter("transactions_processed_total", "Total transactions processed")


def metrics_endpoint():
    return Response(content=generate_latest(), media_type="text/plain")


def track_requests(app):
    @app.middleware("http")
    async def metrics_middleware(request: Callable, call_next):
        method = request.method
        path = request.url.path
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        http_requests_total.labels(method=method, endpoint=path, status=response.status_code).inc()
        http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)

        return response
