from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import sentry_sdk
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.infrastructure.database.session import sessionmanager
from app.infrastructure.cache.redis import redis_client
from app.infrastructure.event_bus.redis_event_bus import RedisEventBus
from app.infrastructure.logging.structlog_setup import configure_logging
from app.infrastructure.metrics.prometheus import metrics_app
from app.infrastructure.tracing.opentelemetry import setup_tracing
from app.infrastructure.sentry import init_sentry
from app.interfaces.api.middleware import (
    RequestIDMiddleware, LoggingMiddleware, SecurityHeadersMiddleware, RateLimitMiddleware,
    CSPMiddleware, SessionMiddleware, SubscriptionEnforcementMiddleware, AuditLogMiddleware
)
from app.interfaces.api.errors import (
    validation_exception_handler, integrity_error_handler, sqlalchemy_error_handler,
    jwt_error_handler, taxflow_error_handler, generic_exception_handler, http_exception_handler
)
from app.interfaces.api.routers import (
    auth, users, clients, transactions, receipts, analytics, affiliate, webhooks, admin, health,
    subscription, billing, export, teams, portal, coupons, gdpr, integrations, search
)
from app.interfaces.api.websocket import websocket_router
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from jose import JWTError
from app.common.exceptions import TaxFlowError
from starlette.exceptions import HTTPException
from starlette.requests import Request
import structlog

logger = structlog.get_logger()

# Global event bus instance
event_bus = RedisEventBus()

# Initialize Sentry
if settings.SENTRY_DSN:
    init_sentry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()
    setup_tracing()
    logger.info("Starting TaxFlow AI", env=settings.ENVIRONMENT, version=settings.VERSION)

    # Initialize infrastructure
    sessionmanager.init(str(settings.DATABASE_URL))
    await redis_client.initialize()
    await event_bus.init()

    # Register event handlers
    from app.infrastructure.event_handlers import register_handlers
    await register_handlers(event_bus)

    # Start background tasks (optional)
    from app.worker import start_scheduler
    await start_scheduler()

    yield

    # Shutdown
    await sessionmanager.close()
    await redis_client.close()
    await event_bus.close()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # Middleware (order matters)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CSPMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuditLogMiddleware)  # logs all changes
    app.add_middleware(SessionMiddleware)
    app.add_middleware(SubscriptionEnforcementMiddleware)

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(o) for o in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS or ["*"],
    )

    if settings.RATE_LIMIT_ENABLED:
        app.add_middleware(RateLimitMiddleware)

    # Metrics
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        env_var_name="ENABLE_METRICS",
    )
    instrumentator.instrument(app).expose(app, endpoint="/metrics")

    # OpenTelemetry
    FastAPIInstrumentor.instrument_app(app)

    # Exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(JWTError, jwt_error_handler)
    app.add_exception_handler(TaxFlowError, taxflow_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Routers
    api_prefix = settings.API_V1_STR
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(clients.router, prefix=api_prefix)
    app.include_router(transactions.router, prefix=api_prefix)
    app.include_router(receipts.router, prefix=api_prefix)
    app.include_router(analytics.router, prefix=api_prefix)
    app.include_router(affiliate.router, prefix=api_prefix)
    app.include_router(webhooks.router, prefix=api_prefix)
    app.include_router(admin.router, prefix=api_prefix)
    app.include_router(subscription.router, prefix=api_prefix)
    app.include_router(billing.router, prefix=api_prefix)
    app.include_router(export.router, prefix=api_prefix)
    app.include_router(teams.router, prefix=api_prefix)
    app.include_router(portal.router, prefix=api_prefix)
    app.include_router(coupons.router, prefix=api_prefix)
    app.include_router(gdpr.router, prefix=api_prefix)
    app.include_router(integrations.router, prefix=api_prefix)
    app.include_router(search.router, prefix=api_prefix)
    app.include_router(websocket_router)

    return app


app = create_app()
