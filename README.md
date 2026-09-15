# 🇬🇭 Ghana Motivation Backend — Aquaba Enterprise Infrastructure

> **High-Performance, Asynchronous RESTful API Engine for Daily Motivational Delivery, Mobile Offline Sync, and Zero-Trust Paystack Financial Subscriptions.**

[![Python Version](https://img.shields.io/badge/Python-3.10%2B%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI%200.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Validation-Pydantic%20V2-e92063.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0%20Async-d71f00.svg?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20(aiosqlite)%20%7C%20PostgreSQL%20(asyncpg)-4169e1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Security](https://img.shields.io/badge/Hashing-Argon2id%20%2B%20JWT%20Rotation-black.svg?logo=auth0&logoColor=white)](https://argon2-cffi.readthedocs.io/)
[![Payment](https://img.shields.io/badge/Payments-Paystack%20%28Mobile%20Money%20%2B%20Cards%29-09A5DB.svg?logo=paystack&logoColor=white)](https://paystack.com/)
[![Test Suite](https://img.shields.io/badge/Tests-100%25%20Passed%20(Dual--Transport)-brightgreen.svg?logo=checkmarx&logoColor=white)](./tests/)
[![Architecture](https://img.shields.io/badge/Architecture-DDD--Lite%20%7C%20Orchestrator%20Pattern-orange.svg)]()

---

## 📑 Table of Contents
- [1. Executive Summary & Product Vision](#1-executive-summary--product-vision)
- [2. Architectural Pattern & Design Philosophy](#2-architectural-pattern--design-philosophy)
- [3. Core Enterprise Capabilities & Security Safeguards](#3-core-enterprise-capabilities--security-safeguards)
- [4. Technology Stack](#4-technology-stack)
- [5. Project Directory Layout](#5-project-directory-layout)
- [6. Database Schema & Data Models](#6-database-schema--data-models)
- [7. Complete API Reference & Endpoint Catalog](#7-complete-api-reference--endpoint-catalog)
  - [Authentication Domain (`/api/v1/auth`)](#-authentication-domain-apiv1auth)
  - [User Profile & Subscription Status (`/api/v1/users`)](#-user-profile--subscription-status-apiv1users)
  - [Zero-Trust Payment Gateway (`/api/v1/payments`)](#-zero-trust-payment-gateway-apiv1payments)
  - [Quotes Delivery & Offline Caching (`/api/v1/quotes`)](#-quotes-delivery--offline-caching-apiv1quotes)
- [8. Mobile Data Serialization Contract (Epoch Milliseconds)](#8-mobile-data-serialization-contract-epoch-milliseconds)
- [9. Environment Configuration (`.env`)](#9-environment-configuration-env)
- [10. Quick Start & Local Setup](#10-quick-start--local-setup)
- [11. Comprehensive Testing Framework (`tests/`)](#11-comprehensive-testing-framework-tests)
- [12. Production Deployment & Hardening](#12-production-deployment--hardening)
- [13. Troubleshooting & FAQ](#13-troubleshooting--faq)
- [14. License & Architectural Governance](#14-license--architectural-governance)

---

## 1. Executive Summary & Product Vision

The **Ghana Motivation Backend** serves as the mission-critical core powering the **Aquaba Mobile Application** in Ghana and West Africa. It delivers high-impact daily motivational wisdom, manages a server-authoritative 3-day free trial period, orchestrates recurring/one-time Mobile Money and Debit Card payments via **Paystack**, and provides offline batch downloading capabilities so users receive inspiring push notifications even during cellular network blackouts.

Engineered from the ground up on Python 3.10+ and FastAPI, this system is built to enterprise standards: strictly asynchronous, non-blocking I/O throughout, state-of-the-art **Argon2id** password hashing, dual JWT token rotation with reuse theft detection, and server-controlled financial boundaries that reject any client-side monetary tampering.

---

## 2. Architectural Pattern & Design Philosophy

The codebase strictly adheres to **Domain-Driven Design Lite (DDD-Lite)** governed by the **Orchestrator Pattern** and the **Enterprise Python Architecture Constitution**.

```mermaid
graph TD
    Client[Mobile / Web Client] -->|HTTP / JSON| Router[FastAPI Routers]
    Router -->|Pydantic Schema Validation| Service[Service Layer - Orchestrator]
    Service -->|Business Logic & Coordination| Repo[Repository Layer - Specialists]
    Service -->|HTTP Calls| PaystackClient[Paystack Gateway Abstraction]
    Repo -->|SQLAlchemy 2.0 Async| DB[(Async Database - SQLite / PostgreSQL)]
    Service -->|Security Primitives| CoreSecurity[Argon2id / JWT Engine]
```

### Layer Separation & Responsibilities
1. **Public Facade (`__init__.py`):** Every module exposes its public contracts via `__all__` tuples, preventing internal leakage and eliminating circular imports.
2. **Routers (`router.py`):** Entrypoints responsible *only* for HTTP status codes, dependency injection, and Pydantic schema validation. No database or business calculations are permitted inside routers.
3. **Services (`service.py` - The Maestros):** Orchestrate domain workflows, invoke repositories, apply business rules (e.g., trial expiration math, token rotation, subscription date extension), and emit typed domain models.
4. **Repositories (`repo.py` - The Specialists):** Single Responsibility Principle (SRP) data access layer inheriting from `BaseRepository[T]`. Perform isolated SQL queries via SQLAlchemy 2.0.
5. **Schemas (`schema.py`):** Pydantic V2 boundary schemas enforcing type safety, string sanitization, and mobile-compliant epoch serialization.
6. **Core (`GhanaMotivationApp/core/`):** Cross-cutting concerns including security, unified custom exception hierarchy, and standard enums.

---

## 3. Core Enterprise Capabilities & Security Safeguards

### 🛡️ 1. Advanced Authentication & Theft Guard
- **Argon2id Password Hashing:** Replaces obsolete algorithms with memory-hard Argon2id (`argon2-cffi`), neutralizing GPU/ASIC rainbow table attacks.
- **Dual JWT Token Lifecycle:** Short-lived `access_token` (30 minutes) combined with long-lived, database-backed `refresh_token` (30 days).
- **Automated Token Rotation:** Each refresh request invalidates the old refresh token and issues a fresh pair.
- **Token Reuse Detection (Theft Guard):** If a compromised or revoked token is reused by an attacker, the system detects a breach and revokes the entire compromised session chain immediately.
- **Granular Session Revocation:** Supports both single-device logout (`/auth/logout`) and global bulk logout (`/auth/logout-all`).

### ⏱️ 2. Server-Authoritative Trial & Subscription Engine
- **Tamper-Proof Math:** Free trial (3 days) and subscription countdowns are calculated server-side using immutable UTC timestamps. Device clock manipulation has zero effect.
- **Additive Subscription Extension:** Renewals made prior to subscription expiry append 30 days to the *future expiry date* rather than resetting from the current moment, ensuring paying customers never lose prepaid days.

### 💳 3. Zero-Trust Financial Boundaries (Paystack)
- **Zero Client Price Trust:** The client *cannot* submit payment amounts. The server retrieves the authoritative fee (`SUBSCRIPTION_PRICE_GHS`) from verified internal settings.
- **Ownership Boundary Enforcement:** Users cannot verify or inspect transaction references belonging to other accounts (enforced via `403 Forbidden`).
- **Webhook Cryptographic Integrity:** All incoming Paystack webhooks require a valid `X-Paystack-Signature` header computed via HMAC-SHA512 using the server secret key. Fake or mismatched webhooks are rejected with `401 Unauthorized`.
- **Idempotency Safeguard:** Duplicate webhooks or redundant verify requests do not duplicate subscriptions or corrupt user balances.

### 📴 4. Offline Batch Sync for Mobile Clients
- **Batch Range Sync:** Mobile clients can download quotes in custom ranges (e.g., `start_day=1&end_day=30`) to schedule local OS notifications offline for up to an entire year (365 days).
- **Leap-Year Safe:** UTC day 366 automatically clamps to day 365, preventing out-of-bounds database exceptions.

---

## 4. Technology Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| **Runtime** | Python | `3.10+` (Tested on `3.13`) | Core programming language with PEP 695 typing |
| **Web Framework** | FastAPI | `0.115.0+` | High-performance asynchronous REST API framework |
| **ASGI Server** | Uvicorn | `0.30.0+` | Production-grade lightning-fast ASGI web server |
| **Data Validation** | Pydantic V2 | `2.9.0+` | Type validation, serialization, and boundary defense |
| **Configuration** | Pydantic Settings | `2.5.0+` | Twelve-Factor environment variable management |
| **ORM** | SQLAlchemy | `2.0.35+` | Fully asynchronous SQL toolkit and relational mapper |
| **Async DB Driver** | aiosqlite / asyncpg | Latest | Non-blocking database connectors for SQLite and PostgreSQL |
| **Password Hashing** | Argon2id (`argon2-cffi`)| `23.1.0+` | State-of-the-art memory-hard password hashing |
| **Token Engine** | PyJWT | `2.9.0+` | Cryptographically signed JSON Web Tokens (HS256) |
| **HTTP Client** | HTTPX | `0.27.0+` | Async HTTP client for Paystack API and integration testing |

---

## 5. Project Directory Layout

```text
ghana-motivation-backend/
├── GhanaMotivationApp/             # Primary Application Package
│   ├── core/                       # Cross-cutting primitives & infrastructure
│   │   ├── __init__.py             # Public facade
│   │   ├── enums.py                # Finite domain enums (EnvironmentEnum, CurrencyEnum, etc.)
│   │   ├── exceptions.py           # Unified custom exception hierarchy
│   │   └── security.py            # Argon2id hasher & JWT lifecycle management
│   ├── database/                   # Asynchronous database infrastructure
│   │   ├── __init__.py             # Public facade
│   │   ├── base.py                 # Declarative Base & AuditMixin (created_at, updated_at)
│   │   ├── repo.py                 # Generic BaseRepository[T] implementation
│   │   └── session.py              # Async engine, sessionmaker, and dependency provider
│   ├── settings/                   # Centralized configuration
│   │   ├── __init__.py             # Public facade exporting `settings`
│   │   └── s.py                    # Pydantic Settings model with production validators
│   └── modules/                    # Domain-Driven Functional Modules
│       ├── auth/                   # Registration, login, token rotation, logout
│       ├── user/                   # User profile, password rotation, trial status
│       ├── payment/                # Payments, Paystack checkout, webhook handling
│       ├── paystack/               # Paystack API abstraction & Mock Client
│       ├── quote/                  # Daily quotes, random quotes, batch sync
│       └── subscription/           # Subscription ledger & duration management
├── scripts/                        # Administrative and maintenance automation
│   ├── seed_quotes.py              # Seeds 365 curated motivational quotes
│   └── seed_users.py               # Seeds mock users for development testing
├── tests/                          # Automated Integration Test Suite
│   ├── __init__.py                 # Facade exports
│   ├── config.py                   # Smart Dual-Transport engine & ANSI logging
│   ├── run_all_tests.py            # Master Test Orchestrator
│   ├── test_01_auth.py             # Auth domain test suite
│   ├── test_02_users.py            # User domain test suite
│   ├── test_03_payments.py         # Payment & Webhook test suite
│   ├── test_04_quotes.py           # Quote delivery & batch validation test suite
│   └── README.md                   # Dedicated test suite documentation
├── main.py                         # Application factory, middleware & lifespan entrypoint
├── requirements.txt                # Production dependency manifest
├── pyproject.toml                  # Modern package metadata & tool configuration
├── README.md                       # Comprehensive English System Documentation
└── README_AR.md                    # Comprehensive Arabic System Documentation (المستند العربي)
```

---

## 6. Database Schema & Data Models

```mermaid
erDiagram
    USERS ||--o{ REFRESH_TOKENS : has
    USERS ||--o{ PAYMENTS : initiates
    USERS ||--o{ SUBSCRIPTIONS : owns

    USERS {
        int id PK
        string email UK
        string name
        string hashed_password
        string device_fingerprint
        datetime trial_start
        datetime trial_end
        boolean is_premium
        datetime premium_expires
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    REFRESH_TOKENS {
        int id PK
        string token UK
        int user_id FK
        datetime expires_at
        boolean is_revoked
        datetime created_at
    }

    PAYMENTS {
        int id PK
        string reference UK
        int amount
        string currency
        string status
        datetime paid_at
        int user_id FK
        datetime created_at
        datetime updated_at
    }

    SUBSCRIPTIONS {
        int id PK
        int user_id FK
        datetime start_date
        datetime next_billing
        string status
        datetime created_at
        datetime updated_at
    }

    QUOTES {
        int id PK
        int day_number UK
        string content
        string author
        string category
        boolean is_active
        datetime created_at
        datetime updated_at
    }
```

---

## 7. Complete API Reference & Endpoint Catalog

All routes are prefixed with `/api/v1`. Interactive documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### 🛡️ Authentication Domain (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required | Status Codes |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Registers a new user and initiates a 3-day trial | None | `201`, `409`, `422` |
| `POST` | `/api/v1/auth/login` | Authenticates credentials and returns dual token pair | None | `200`, `401`, `422` |
| `POST` | `/api/v1/auth/refresh` | Rotates refresh token, detects reuse theft, issues new pair | None (Body) | `200`, `401`, `422` |
| `POST` | `/api/v1/auth/logout` | Revokes the active refresh token session | Bearer JWT | `200`, `401`, `422` |
| `POST` | `/api/v1/auth/logout-all` | Revokes all active refresh tokens for the current user | Bearer JWT | `200`, `401` |

#### Registration Request Example:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kwame Mensah",
    "email": "kwame@example.com",
    "password": "SecurePassword123!",
    "device_fingerprint": "DEVICE_HW_987654"
  }'
```

#### Login Request Example:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "kwame@example.com",
    "password": "SecurePassword123!"
  }'
```

---

### 👤 User Profile & Subscription Status (`/api/v1/users`)

| Method | Endpoint | Description | Auth Required | Status Codes |
|---|---|---|---|---|
| `GET` | `/api/v1/users/me` | Fetches the profile of the currently authenticated user | Bearer JWT | `200`, `401` |
| `GET` | `/api/v1/users/status` | Real-time calculation of trial and premium subscription flags | Bearer JWT | `200`, `401` |
| `PATCH`| `/api/v1/users/me/password` | Verifies old password, rotates to new Argon2id hash | Bearer JWT | `200`, `401`, `422` |

#### User Status Response Example:
```json
{
  "user": {
    "id": 1,
    "email": "kwame@example.com",
    "name": "Kwame Mensah",
    "device_fingerprint": "DEVICE_HW_987654",
    "trial_start": 1788214785232,
    "trial_end": 1788473985232,
    "is_premium": false,
    "premium_expires": null,
    "is_active": true,
    "created_at": 1788214785232,
    "updated_at": 1788214785232
  },
  "trial_remaining_seconds": 259199,
  "is_trial_active": true,
  "is_premium": false,
  "premium_expires": null
}
```

---

### 💳 Zero-Trust Payment Gateway (`/api/v1/payments`)

| Method | Endpoint | Description | Auth Required | Status Codes |
|---|---|---|---|---|
| `POST` | `/api/v1/payments/initialize` | Creates Paystack checkout session using server-authoritative price | Bearer JWT | `200`, `401` |
| `GET` | `/api/v1/payments/verify` | Verifies Paystack reference, activates 30-day premium (Idempotent) | Bearer JWT | `200`, `401`, `403`, `404` |
| `POST` | `/api/v1/payments/webhook` | Handles Paystack asynchronous webhooks with HMAC-SHA512 signature | HMAC Header | `200`, `401` |

#### Initialize Payment Request:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/initialize" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"payment_method": "mobile_money"}'
```

#### Response:
```json
{
  "authorization_url": "https://checkout.paystack.com/mock/MOCK-A1B2C3D4E5F6",
  "reference": "MOCK-A1B2C3D4E5F6"
}
```

---

### 💡 Quotes Delivery & Offline Caching (`/api/v1/quotes`)

| Method | Endpoint | Description | Auth Required | Status Codes |
|---|---|---|---|---|
| `GET` | `/api/v1/quotes/today` | Fetches the motivational quote for the current UTC day of the year | None | `200`, `404` |
| `GET` | `/api/v1/quotes/random` | Returns a random active motivational quote | None | `200`, `404` |
| `GET` | `/api/v1/quotes/batch` | Range query (`start_day` to `end_day`) for mobile offline caching | None | `200`, `422` |

#### Batch Download Example (Days 1 to 7):
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/quotes/batch?start_day=1&end_day=7"
```

---

## 8. Mobile Data Serialization Contract (Epoch Milliseconds)

To ensure seamless, cross-platform compatibility with the Flutter/Dart mobile client:

> ⚠️ **CRITICAL CONTRACT:** All datetime timestamps (`created_at`, `updated_at`, `trial_start`, `trial_end`, `premium_expires`, `paid_at`) crossing the API boundary are serialized as **64-bit Integer Unix Epoch Milliseconds** (e.g., `1788214785232`), **NEVER** ISO 8601 string representations.

This eliminates client-side timezone parsing ambiguities across diverse Android and iOS runtime environments.

---

## 9. Environment Configuration (`.env`)

The application is configured using Pydantic Settings. All variables can be defined in a `.env` file at the project root:

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENVIRONMENT` | `str` | `development` | Runtime environment (`development`, `staging`, `production`). In production, placeholder keys trigger immediate startup crashes. |
| `HOST` | `str` | `127.0.0.1` | Network interface to bind the Uvicorn server to. |
| `PORT` | `int` | `8000` | Listening TCP port number. |
| `RELOAD` | `bool` | `False` | Auto-reload server upon code change (Development only). |
| `API_PREFIX` | `str` | `/api/v1` | Global URL prefix for all REST endpoints. |
| `DATABASE_URL` | `str` | `sqlite+aiosqlite:///./test.db` | Async database URI. Use `postgresql+asyncpg://user:pass@host/db` for production. |
| `ECHO` | `bool` | `False` | Enable verbose SQLAlchemy raw SQL console logging. |
| `SECRET_KEY` | `str` | `*required in prod*` | Cryptographic secret key for signing JWT Access Tokens. |
| `REFRESH_SECRET_KEY`| `str` | `*required in prod*` | Separate secret key for signing JWT Refresh Tokens. |
| `ALGORITHM` | `str` | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | `30` | Access Token lifetime in minutes. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `int` | `30` | Refresh Token lifetime in days. |
| `PAYSTACK_SECRET_KEY` | `str` | `*required in prod*` | Secret key provided by Paystack Dashboard. |
| `PAYSTACK_PUBLIC_KEY` | `str` | `*required in prod*` | Public key provided by Paystack Dashboard. |
| `PAYSTACK_MODE` | `str` | `mock` | `mock` (emulates Paystack locally without network calls) or `live`. |
| `TRIAL_DAYS` | `int` | `3` | Free trial period duration in days. |
| `SUBSCRIPTION_DAYS` | `int` | `30` | Duration of each paid subscription cycle in days. |
| `SUBSCRIPTION_AMOUNT_PESEWAS` | `int` | `1000` | Authoritative subscription cost in Pesewas (1000 Pesewas = 10 GHS). |

---

## 10. Quick Start & Local Setup

### 1. Prerequisites
- Python `3.10` or higher (Python `3.11` to `3.13` recommended).
- Git installed on host machine.

### 2. Environment Setup
```powershell
# 1. Clone the repository
git clone <repository-url>
cd ghana-motivation-backend

# 2. Create and activate a Python virtual environment
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate

# 3. Upgrade pip and install all production dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Database Initialization & Quote Seeding
Before launching the server, initialize the database and seed the 365 daily quotes:
```powershell
python scripts/seed_quotes.py
```

### 4. Launching the Development Server
```powershell
python main.py
# Or directly via Uvicorn:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to access the interactive OpenAPI documentation.

---

## 11. Comprehensive Testing Framework (`tests/`)

The repository includes an enterprise-grade integration test suite located in `tests/`. It utilizes a **Smart Dual-Transport Strategy**:
1. **Live HTTP Mode:** Automatically connects to `http://127.0.0.1:8000` if the server is running.
2. **In-Memory ASGI Fallback Mode:** If no server is running, it seamlessly executes tests in-memory via `httpx.ASGITransport(app=main.app)`.

### Run the Master Test Pipeline
```powershell
python tests/run_all_tests.py
```

### Run Individual Domain Suites
```powershell
# Authentication & Sessions
python tests/test_01_auth.py

# User Profiles & Password Rotation
python tests/test_02_users.py

# Payments, Ownership Boundaries & Webhooks
python tests/test_03_payments.py

# Quotes Delivery & Batch Offline Sync
python tests/test_04_quotes.py
```

For complete diagnostic guides and troubleshooting steps, refer to [tests/README.md](file:///d:/_Python%20Projects-27-05-2026/ghana-motivation-backend/tests/README.md).

---

## 12. Production Deployment & Hardening

When promoting to staging and production:
1. **Switch Database to PostgreSQL:**
   ```env
   DATABASE_URL=postgresql+asyncpg://db_user:db_password@db-host:5432/ghana_motivation_prod
   ```
2. **Set Production Mode:**
   ```env
   ENVIRONMENT=production
   PAYSTACK_MODE=live
   ```
3. **Run via Production Gunicorn / Uvicorn Workers:**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
4. **Enforce HTTPS & Reverse Proxy:** Place behind Nginx, Caddy, or Cloudflare with SSL termination and HSTS enabled.

---

## 13. Troubleshooting & FAQ

### Q1: Why does `/quotes/today` return `404 Not Found`?
**Cause:** The database was created without seeding the 365 daily quotes.
**Fix:** Run `python scripts/seed_quotes.py`.

### Q2: Why does `PATCH /users/me/password` return `405 Method Not Allowed`?
**Cause:** Attempting to call the endpoint using `PUT` or `POST`.
**Fix:** The password rotation endpoint strictly requires the HTTP `PATCH` method.

### Q3: Why does payment verification return `403 Forbidden`?
**Cause:** Ownership protection triggered. User A cannot verify or claim a payment reference generated by User B.
**Fix:** Ensure the `Authorization: Bearer <token>` matches the user who initialized the payment.

---

## 14. License & Architectural Governance

This software is developed and maintained under strict architectural guidelines. All modifications must comply with the Enterprise Python Architecture Constitution:
- Modern Python 3.10+ union pipe syntax (`|`). Legacy `Union` and `Optional` are strictly forbidden.
- Pydantic V2 boundary models for all inbound and outbound contracts.
- Explicit `__all__` facade patterns in every package directory.
- Zero client-trust for financial calculations.

---
*Built with precision for the Aquaba Motivation Ecosystem.*
