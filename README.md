TaxFlow AI – Complete Production-Ready Codebase

📋 Table of Contents

· Overview
· The Problem It Solves
· Key Features
· Technology Stack
· Architecture
· Project Structure
· Installation Guide
  · Prerequisites
  · Local Development Setup
  · Docker Setup
  · Environment Variables
· Usage & API Documentation
· Screenshots
· Roadmap
· Contributing
· License

---

Overview

TaxFlow AI is an AI‑powered tax automation platform designed for freelancers, small businesses, and accounting professionals. It combines intelligent receipt scanning, automatic transaction categorization, subscription billing, an affiliate program, and seamless integrations (QuickBooks, Stripe) into one scalable, production‑ready backend.

This repository contains the complete, regenerated codebase v9.0.0 – a full architectural overhaul from the ground up. It is built with modern Python (FastAPI, SQLAlchemy 2.0, Pydantic v2), follows Domain‑Driven Design principles, and includes every feature needed to launch a SaaS product: user management, MFA, teams, GDPR compliance, background jobs, observability, and more.

---

The Problem It Solves

Managing finances and taxes is a huge pain for small businesses and freelancers. They juggle:

· Receipts – paper, email, scanned images – all need to be stored and linked to transactions.
· Transaction categorization – manually assigning tax categories (e.g., “advertising”, “meals”) is time‑consuming and error‑prone.
· Subscription billing – tracking who paid, handling upgrades/downgrades, and managing invoices.
· Integrations – exporting data to QuickBooks or other accounting software is often manual.
· Affiliate programs – many platforms lack built‑in referral systems to help businesses grow.
· GDPR compliance – users need the right to access and delete their data.

TaxFlow AI solves all of this in one unified platform:

· Users upload receipts – the system extracts text via OCR and uses OpenAI GPT‑4o to automatically categorize transactions.
· Subscriptions are handled via Stripe – including trials, coupons, and proration.
· An affiliate program lets users earn commissions by referring others.
· QuickBooks integration syncs categorized transactions directly.
· GDPR tools allow users to export or delete all their data with one click.
· Everything is secured with MFA, rate limiting, and audit logs.

---

Key Features

· 🔐 Authentication & Security
  · Email/password registration with email verification
  · Multi‑factor authentication (TOTP) with recovery codes
  · JWT access & refresh tokens, session management
  · Rate limiting, CSP headers, CORS, trusted hosts
  · Account lockout after failed attempts
· 👥 User Management
  · Profile update, preferences, timezone
  · Soft delete & GDPR data deletion
  · Activity logging and audit trails
· 🧾 Clients & Transactions
  · Manage clients and their tax information
  · Create, update, delete transactions
  · Bulk operations, duplicate detection
  · AI‑powered categorization (OpenAI) with confidence scores
  · Manual override and review workflow
· 📄 Receipts & OCR
  · Upload receipts (PDF, images) to AWS S3
  · Asynchronous OCR processing (textract or custom)
  · Link receipts to transactions
· 💳 Subscriptions & Billing
  · Stripe integration for customers, subscriptions, invoices
  · Support for monthly/yearly plans, coupons
  · Webhook handling (idempotent, retry logic)
  · Usage limits per subscription tier
· 🤝 Affiliate Program
  · Referral codes and commission tracking
  · Withdrawal requests (Stripe Connect, PayPal, bank transfer)
  · Admin approval and automated payouts
  · Payout batching and history
· 🔌 Integrations
  · QuickBooks Online OAuth2 flow
  · Sync transactions to QuickBooks purchases
  · Token refresh (stubbed, needs implementation)
· 👪 Teams
  · Create teams, invite members, assign roles
  · Shared access to clients and transactions
· 📊 Export & GDPR
  · Export transactions as CSV/Excel
  · Full GDPR data export (JSON + receipt files) as ZIP
  · Automated data deletion after grace period
· 🔍 Search
  · Full‑text search across transactions, clients, receipts (PostgreSQL)
  · Optional Elasticsearch support
· 🛠️ Admin Panel
  · Manage withdrawals, coupons, users
  · View audit logs and background jobs
· 📈 Observability
  · Structured logging (structlog) with JSON format
  · Prometheus metrics, OpenTelemetry tracing, Sentry
  · Health checks and readiness probes
· ⏰ Background Jobs
  · Celery workers for async tasks (exports, payouts, digests)
  · Scheduled tasks (reset monthly usage, cleanup sessions)
· 🌐 Real‑time Updates
  · WebSocket connections for live notifications
  · Redis pub/sub for cross‑instance events

---

Technology Stack

Layer Technologies
Backend Python 3.12, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, Celery, Redis, PostgreSQL + pgvector
AI & OCR OpenAI API (GPT-4o, embeddings), textract (fallback), Pillow, pdfplumber
Storage AWS S3 (or MinIO for dev), boto3, aioboto3
Payments Stripe (subscriptions, Connect)
Integrations QuickBooks Online OAuth2 (httpx-oauth)
Security Argon2 password hashing, pyotp (MFA), python-jose (JWT), cryptography, passlib
Observability structlog, prometheus-client, opentelemetry, sentry-sdk
Infrastructure Docker, Docker Compose, Traefik (prod), pgvector, Redis Stack
Testing pytest, pytest-asyncio, factory-boy, faker, respx, locust (load testing)

---

Architecture

TaxFlow AI follows a Domain‑Driven Design (DDD) layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (Interfaces)                   │
│  FastAPI routers, WebSockets, middleware, dependencies       │
├─────────────────────────────────────────────────────────────┤
│                   Application Layer (Use Cases)              │
│  Orchestrates domain entities, repositories, and services    │
├─────────────────────────────────────────────────────────────┤
│                     Domain Layer (Core)                      │
│  Entities, Value Objects, Domain Events, Repository interfaces│
├─────────────────────────────────────────────────────────────┤
│                Infrastructure Layer (Adapters)               │
│  Database repositories, caching, event bus, email, storage   │
│  External services: Stripe, OpenAI, QuickBooks, AWS S3       │
└─────────────────────────────────────────────────────────────┘
```

Key Design Decisions

· Rich Domain Models – Business logic lives in entities (e.g., User, Transaction), which emit domain events when state changes.
· Repository Pattern – Abstracts data access; implementations in infrastructure (SQLAlchemy, Redis).
· CQRS‑like – Use cases handle commands/queries; read models are simple DTOs.
· Event‑Driven – Domain events are published via Redis pub/sub, allowing asynchronous side effects (notifications, analytics, etc.).
· Dependency Inversion – All external dependencies are injected via use case constructors.
· Background Processing – Long‑running tasks (OCR, exports, payouts) are offloaded to Celery.
· Idempotency & Reliability – Webhooks use idempotency keys; Celery tasks have retries and time limits.

Data Flow Example (Transaction Categorization)

1. User uploads receipt → POST /receipts/upload → saved to S3 → background job starts.
2. OCR task processes image → extracts text → creates transaction.
3. CategorizeTransactionUseCase calls OpenAICategorizer → returns category/confidence.
4. Transaction entity is updated → emits TransactionCategorized event.
5. Event handler sends notification to user (if confidence low) and updates analytics.
6. API returns categorized transaction to client.

---

Project Structure

```
taxflow-ai/
├── .env.example                     # Environment variables template
├── .gitignore
├── alembic.ini                      # Alembic configuration
├── alembic/                          # Database migrations
│   ├── env.py
│   ├── versions/
│   │   ├── 001_initial_migration.py
│   │   └── 002_add_indexes_and_triggers.py
├── backend/                          # Main application code
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app factory
│   │   ├── config.py                  # Pydantic settings
│   │   ├── common/                     # Shared utilities
│   │   │   └── exceptions.py
│   │   ├── domain/                     # Domain layer
│   │   │   ├── entities/               # Domain entities
│   │   │   │   ├── user.py
│   │   │   │   ├── transaction.py
│   │   │   │   ├── receipt.py
│   │   │   │   └── ... (20+ files)
│   │   │   ├── value_objects/          # Value objects
│   │   │   │   ├── email.py
│   │   │   │   ├── money.py
│   │   │   │   └── tax_category.py
│   │   │   ├── events/                 # Domain events
│   │   │   │   └── domain_events.py
│   │   │   └── repositories/            # Repository interfaces
│   │   │       ├── user.py
│   │   │       ├── transaction.py
│   │   │       └── ...
│   │   ├── application/                 # Application layer
│   │   │   ├── dtos.py                   # Data transfer objects
│   │   │   └── use_cases/                 # Use cases (organized by feature)
│   │   │       ├── auth/
│   │   │       │   ├── register.py
│   │   │       │   ├── login.py
│   │   │       │   └── ...
│   │   │       ├── transactions/
│   │   │       │   ├── categorize.py
│   │   │       │   └── ...
│   │   │       ├── affiliate/
│   │   │       ├── export/
│   │   │       ├── gdpr/
│   │   │       ├── quickbooks/
│   │   │       └── ...
│   │   ├── infrastructure/               # Infrastructure layer
│   │   │   ├── database/
│   │   │   │   ├── models.py              # SQLAlchemy models
│   │   │   │   ├── session.py              # DB session manager
│   │   │   │   └── repositories/           # SQLAlchemy implementations
│   │   │   │       ├── user.py
│   │   │   │       └── ...
│   │   │   ├── cache/
│   │   │   │   └── redis.py
│   │   │   ├── event_bus/
│   │   │   │   └── redis_event_bus.py
│   │   │   ├── email/
│   │   │   │   └── smtp_sender.py
│   │   │   ├── storage/
│   │   │   │   └── s3.py
│   │   │   ├── ai/
│   │   │   │   └── openai.py
│   │   │   ├── payment/
│   │   │   │   └── stripe.py
│   │   │   ├── logging/
│   │   │   │   └── structlog_setup.py
│   │   │   ├── metrics/
│   │   │   │   └── prometheus.py
│   │   │   ├── tracing/
│   │   │   │   └── opentelemetry.py
│   │   │   ├── sentry.py
│   │   │   ├── event_handlers.py
│   │   │   └── background/
│   │   │       ├── celery_app.py
│   │   │       └── tasks.py
│   │   └── interfaces/                    # Interface layer
│   │       ├── api/
│   │       │   ├── dependencies.py
│   │       │   ├── middleware.py
│   │       │   ├── errors.py
│   │       │   ├── routers/
│   │       │   │   ├── auth.py
│   │       │   │   ├── transactions.py
│   │       │   │   ├── affiliate.py
│   │       │   │   ├── admin/
│   │       │   │   │   └── withdrawals.py
│   │       │   │   ├── integrations.py
│   │       │   │   ├── search.py
│   │       │   │   └── ...
│   │       │   └── websocket.py
│   └── worker/                             # Celery worker entry point (if separate)
│       └── celery_app.py (symlink or separate)
├── docker-compose.yml              # Development compose
├── docker-compose.prod.yml          # Production compose
├── pyproject.toml                   # Dependencies (Poetry)
└── README.md                        # This file
```

---

Installation Guide

Prerequisites

· Python 3.12+
· Poetry (for dependency management)
· Docker & Docker Compose (optional, for local services)
· PostgreSQL 17+ with pgvector (if running without Docker)
· Redis 7+
· AWS S3 bucket (or MinIO for development)
· Stripe account (for payments)
· OpenAI API key (for AI categorization)
· QuickBooks Developer account (for integration)

Local Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/your-org/taxflow-ai.git
   cd taxflow-ai
   ```
2. Install dependencies using Poetry
   ```bash
   poetry install
   ```
3. Set up environment variables
   · Copy .env.example to .env and fill in your values.
   ```bash
   cp .env.example .env
   ```
4. Start required services (PostgreSQL, Redis, MinIO, etc.)
   ```bash
   docker-compose up -d db redis minio
   ```
5. Run database migrations
   ```bash
   poetry run alembic upgrade head
   ```
6. Start the FastAPI development server
   ```bash
   poetry run uvicorn app.main:app --reload
   ```
7. (Optional) Start Celery worker
   ```bash
   poetry run celery -A app.worker.celery_app worker --loglevel=info
   ```
8. Access the API at http://localhost:8000/docs

Docker Setup

For a fully containerized development environment:

```bash
docker-compose up -d
```

This starts:

· PostgreSQL with pgvector
· Redis Stack (with RedisInsight)
· Jaeger (tracing)
· MinIO (S3-compatible storage)
· MailHog (email testing)
· Flower (Celery monitoring)
· Elasticsearch (optional)

The FastAPI app will be available at http://localhost:8000.

Production Deployment

Use docker-compose.prod.yml with Traefik as reverse proxy. You'll need to:

· Set valid domain names and SSL certificates (Traefik handles Let's Encrypt).
· Configure environment variables securely (use Docker secrets or a vault).
· Ensure S3 buckets, Stripe keys, etc. are set correctly.
· Run with:
  ```bash
  docker-compose -f docker-compose.prod.yml up -d
  ```

Environment Variables

Key variables you must configure:

Variable Description
SECRET_KEY 32‑byte random hex string (for JWT)
ENCRYPTION_KEY 32‑byte base64 key (for Fernet)
DATABASE_URL PostgreSQL async connection string
REDIS_URL Redis connection URL
OPENAI_API_KEY Your OpenAI API key
STRIPE_SECRET_KEY Stripe secret key
STRIPE_WEBHOOK_SECRET Stripe webhook signing secret
AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY AWS credentials for S3
QUICKBOOKS_CLIENT_ID / SECRET QuickBooks OAuth app credentials
SMTP_* Email settings (SendGrid, etc.)
SENTRY_DSN Sentry DSN for error tracking

See .env.example for a complete list.

---

Usage & API Documentation

Once the server is running, interactive API documentation is available at:

· Swagger UI: http://localhost:8000/docs
· ReDoc: http://localhost:8000/redoc

Quick API Walkthrough

1. Register a user
      POST /api/v1/auth/register
      Body: { "email": "user@example.com", "password": "secret", "full_name": "John Doe" }
2. Login
      POST /api/v1/auth/login
      Body: { "email": "...", "password": "..." }
      Returns access and refresh tokens.
3. Create a client
      POST /api/v1/clients
      Headers: Authorization: Bearer <access_token>
      Body: { "name": "Acme Inc", "tax_year": 2025 }
4. Add a transaction
      POST /api/v1/transactions
      Body: { "client_id": 1, "date": "2025-03-20", "description": "Office supplies", "amount": 123.45 }
5. Upload a receipt
      POST /api/v1/receipts/upload?client_id=1
      (multipart/form-data with file)
6. Categorize a transaction
      POST /api/v1/transactions/1/categorize
      The AI will automatically categorize it.
7. Check affiliate balance
      GET /api/v1/affiliate/balance
8. Request a withdrawal
      POST /api/v1/affiliate/withdrawals
      Body: { "amount": 50.00, "method": "stripe_connect" }

For full details, explore the Swagger UI.

---

Screenshots

Note: Replace these placeholders with actual screenshots from your running application.

Feature Description
Dashboard screenshots/dashboard.png Overview of recent transactions, balance, and quick actions.
Transaction List screenshots/transactions.png Filterable list of transactions with AI‑suggested categories.
Receipt Upload screenshots/upload.png Drag‑and‑drop interface for uploading receipts.
AI Categorization screenshots/ai.png Transaction detail showing AI‑generated category and confidence.
Affiliate Dashboard screenshots/affiliate.png Earnings, referral link, and withdrawal history.
QuickBooks Integration screenshots/quickbooks.png Connect your QuickBooks account and sync transactions.
Admin Panel screenshots/admin.png Manage withdrawals, coupons, and users.
API Docs screenshots/swagger.png Interactive Swagger UI for exploring the API.

---

Roadmap

✅ Completed (v9.0.0)

· Core user authentication & MFA
· Client & transaction management
· Receipt upload & OCR processing
· AI‑powered transaction categorization (OpenAI)
· Stripe subscription billing & webhooks
· Affiliate program (commissions, withdrawals)
· QuickBooks OAuth integration
· Teams & role‑based access
· Data export (CSV/Excel) & GDPR compliance
· Full‑text search (PostgreSQL)
· Background jobs with Celery
· Observability (logging, metrics, tracing, Sentry)
· Production‑grade Docker setup

🚧 In Progress (v9.1.0)

· Duplicate transaction detection – improved fuzzy matching
· QuickBooks token refresh – automatic refresh when expired
· Bulk operations – bulk categorize, delete, export
· Unit & integration tests – aiming for >80% coverage
· Frontend reference implementation (React/Next.js)

🔮 Planned (v9.2.0+)

· Mobile app (iOS/Android) for receipt capture on the go
· Advanced analytics – tax summaries, projections
· Multi‑currency support for international users
· Document management – store W-9s, contracts
· Machine learning fine‑tuning – improve categorization with user feedback
· Elasticsearch for enhanced search capabilities
· Webhooks for partners – real‑time data sync

---

Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: git checkout -b feature/amazing-feature.
3. Commit your changes: git commit -m 'Add amazing feature'.
4. Push to the branch: git push origin feature/amazing-feature.
5. Open a Pull Request.

Development Guidelines

· Follow the existing code style (black, ruff, mypy).
· Write tests for new use cases.
· Update documentation (this README, docstrings).
· Ensure all checks pass (CI will run).

---

License

This project is Proprietary – all rights reserved. See the LICENSE file for details.

---

TaxFlow AI – The ultimate foundation for your tax automation SaaS.
Built with ❤️ by the TaxFlow team.
