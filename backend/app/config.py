from typing import List, Optional, Union, Dict, Any
from pydantic import Field, PostgresDsn, RedisDsn, SecretStr, field_validator, EmailStr, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TaxFlow AI"
    VERSION: str = "9.0.0"
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = []
    TRUSTED_HOSTS: Union[str, List[str]] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def parse_trusted_hosts(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [host.strip() for host in v.split(",") if host.strip()]
        return v

    # Security
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_ALGORITHM: str = "argon2id"
    ARGON2_TIME_COST: int = 2
    ARGON2_MEMORY_COST: int = 19456
    ARGON2_PARALLELISM: int = 1
    MFA_ISSUER_NAME: str = "TaxFlow AI"
    ENCRYPTION_KEY: SecretStr
    MFA_RECOVERY_CODES_COUNT: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_LOCKOUT_MINUTES: int = 15
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    SESSION_EXPIRE_DAYS: int = 30
    SESSION_COOKIE_SAMESITE: str = "lax"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_DOMAIN: Optional[str] = None
    CSP_DIRECTIVES: str = "default-src 'self'; script-src 'self' 'unsafe-inline' https://js.stripe.com https://cdn.mxpnl.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.stripe.com https://api.mixpanel.com;"
    SECURITY_CONTACT: EmailStr = "security@taxflow.ai"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_STRICT: str = "5/minute"
    RATE_LIMIT_STORAGE_URI: str = "redis://redis:6379/3"

    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "taxflow"
    DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_ECHO: bool = False
    DATABASE_STATEMENT_TIMEOUT: int = 30000  # milliseconds
    DATABASE_QUERY_TIMEOUT: int = 30  # seconds

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        ).unicode_string()

    # Redis
    REDIS_URL: RedisDsn = "redis://:redispass@redis:6379/0"
    REDIS_PASSWORD: str = "redispass"
    REDIS_MAX_CONNECTIONS: int = 50
    CELERY_BROKER_URL: RedisDsn = "redis://:redispass@redis:6379/1"
    CELERY_RESULT_BACKEND: RedisDsn = "redis://:redispass@redis:6379/2"

    # OpenAI
    OPENAI_API_KEY: Optional[SecretStr] = None
    OPENAI_MODEL: str = "gpt-4o-latest"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CATEGORIZATION_CACHE_TTL: int = 604800
    OPENAI_REQUEST_TIMEOUT: int = 30
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_FALLBACK_MODEL: str = "gpt-3.5-turbo"

    # Stripe
    STRIPE_SECRET_KEY: Optional[SecretStr] = None
    STRIPE_WEBHOOK_SECRET: Optional[SecretStr] = None
    STRIPE_API_VERSION: str = "2025-02-24.acacia"
    STRIPE_PRICE_PRO: Optional[str] = None
    STRIPE_PRICE_FIRM: Optional[str] = None
    STRIPE_PRICE_PRO_YEARLY: Optional[str] = None
    STRIPE_PRICE_FIRM_YEARLY: Optional[str] = None
    STRIPE_CONNECT_CLIENT_ID: Optional[str] = None
    STRIPE_CONNECT_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_TAX_ENABLED: bool = False
    STRIPE_TAX_CODE: Optional[str] = None
    STRIPE_WEBHOOK_TOLERANCE: int = 300

    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "taxflow-receipts-prod"
    AWS_S3_EXPORT_BUCKET: str = "taxflow-exports"
    AWS_S3_ENDPOINT_URL: Optional[str] = None
    AWS_CLOUDFRONT_DOMAIN: Optional[str] = None
    AWS_S3_MAX_CONNECTIONS: int = 25

    # Affiliate
    AFFILIATE_COMMISSION_RATE: float = 0.20
    AFFILIATE_MIN_WITHDRAWAL: int = 1000  # cents
    AFFILIATE_COOKIE_DAYS: int = 30
    FRONTEND_URL: str = "http://localhost:5173"
    AFFILIATE_PAYOUT_METHODS: List[str] = ["stripe_connect", "paypal", "bank_transfer"]
    AFFILIATE_AUTO_PAYOUT_THRESHOLD: int = 5000
    AFFILIATE_AUTO_PAYOUT_CRON: str = "0 9 * * 1"
    ENABLE_AFFILIATE_AUTO_PAYOUT: bool = True

    # File upload
    MAX_UPLOAD_SIZE: int = 52428800  # 50 MB
    ALLOWED_EXTENSIONS: List[str] = ["csv", "xlsx", "pdf", "jpg", "png", "jpeg", "tiff"]
    OCR_PROCESSOR: str = "textract"
    OCR_MAX_RETRIES: int = 3
    OCR_CONCURRENT_TASKS: int = 5

    # Tracing
    OTEL_SERVICE_NAME: str = "taxflow-api"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://jaeger:4318"
    OTEL_TRACES_EXPORTER: str = "otlp"
    OTEL_METRICS_EXPORTER: str = "prometheus"

    # Feature flags
    ENABLE_AI_CATEGORIZATION: bool = True
    ENABLE_AUDIT_LOG: bool = True
    ENABLE_PGVECTOR_SEARCH: bool = True
    ENABLE_TEAMS: bool = True
    ENABLE_CLIENT_PORTAL: bool = True
    ENABLE_QUICKBOOKS_INTEGRATION: bool = True

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    EMAIL_FROM: str = "noreply@taxflow.ai"
    EMAIL_VERIFICATION_REQUIRED: bool = True
    EMAIL_TEMPLATE_DIR: str = "app/infrastructure/email/templates"
    EMAIL_BATCH_SIZE: int = 50
    EMAIL_RATE_LIMIT: str = "100/minute"
    EMAIL_BOUNCE_WEBHOOK_SECRET: Optional[str] = None
    EMAIL_BOUNCE_WEBHOOK_URL: Optional[AnyHttpUrl] = None
    EMAIL_DKIM_SELECTOR: Optional[str] = None
    EMAIL_DKIM_DOMAIN: Optional[str] = None
    EMAIL_DKIM_PRIVATE_KEY_PATH: Optional[str] = None

    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "production"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.2

    # Cookie consent
    COOKIE_CONSENT_ENABLED: bool = True
    COOKIE_CONSENT_BANNER_MESSAGE: str = "We use cookies to enhance your experience."
    COOKIE_CONSENT_PRIVACY_POLICY_URL: str = "/privacy"
    COOKIE_CONSENT_TERMS_URL: str = "/terms"

    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_S3_BUCKET: str = "taxflow-backups"
    BACKUP_SCHEDULE: str = "0 2 * * *"
    BACKUP_RETENTION_DAYS: int = 30

    # Integrations
    QUICKBOOKS_CLIENT_ID: Optional[str] = None
    QUICKBOOKS_CLIENT_SECRET: Optional[SecretStr] = None
    QUICKBOOKS_REDIRECT_URI: Optional[AnyHttpUrl] = None
    QUICKBOOKS_ENVIRONMENT: str = "sandbox"

    # Webhooks
    WEBHOOK_IDEMPOTENCY_CACHE_TTL: int = 86400  # 24 hours
    WEBHOOK_MAX_RETRIES: int = 3
    WEBHOOK_RETRY_BACKOFF_FACTOR: int = 2
    WEBHOOK_RETRY_MAX_DELAY: int = 3600

    # Analytics
    MIXPANEL_TOKEN: Optional[str] = None
    MIXPANEL_API_HOST: str = "https://api.mixpanel.com"

    # Search
    SEARCH_ENGINE: str = "postgresql"  # or elasticsearch
    ELASTICSEARCH_HOST: Optional[str] = None

    # Celery
    CELERY_TASK_ALWAYS_EAGER: bool = False
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3000
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 1000

    # New Relic
    NEW_RELIC_LICENSE_KEY: Optional[str] = None
    NEW_RELIC_APP_NAME: Optional[str] = None

    # Datadog
    DD_API_KEY: Optional[str] = None
    DD_SITE: str = "datadoghq.com"


settings = Settings()  # type: ignore
