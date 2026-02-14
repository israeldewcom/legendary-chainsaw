from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import uuid
import time
from typing import Optional
from app.infrastructure.cache.redis import redis_client
from app.config import settings
from app.common.exceptions import RateLimitExceededError
import structlog

logger = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            "Request processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
            request_id=getattr(request.state, "request_id", None),
            ip=request.client.host if request.client else None,
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = settings.CSP_DIRECTIVES
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.redis = redis_client

    async def dispatch(self, request: Request, call_next):
        # Determine rate limit key based on path and user
        client_ip = request.client.host if request.client else "unknown"
        # Could also use user_id if authenticated
        key = f"rate_limit:{request.method}:{request.url.path}:{client_ip}"

        # Get rate limit config
        if request.url.path.startswith("/api/v1/auth"):
            limit_str = settings.RATE_LIMIT_AUTH
        elif request.url.path.startswith("/api/v1/admin"):
            limit_str = settings.RATE_LIMIT_STRICT
        else:
            limit_str = settings.RATE_LIMIT_DEFAULT

        # Parse "X/minute"
        count, period = limit_str.split("/")
        max_requests = int(count)
        window = 60 if period == "minute" else 1

        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window)

        if current > max_requests:
            raise RateLimitExceededError("Rate limit exceeded")

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_requests - current))
        return response


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Could manage session cookies for web clients
        response = await call_next(request)
        # Not implemented fully
        return response


class SubscriptionEnforcementMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if user is authenticated and enforce limits
        # This is a placeholder
        response = await call_next(request)
        return response


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log all state-changing requests for audit
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # In a real implementation, we'd capture request body and response
            pass
        response = await call_next(request)
        return response
