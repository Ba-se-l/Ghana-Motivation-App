# 🇬🇭 Ghana Motivation Backend — Aquaba App Infrastructure
> **Enterprise-Grade FastAPI Asynchronous Backend Infrastructure for Daily Motivation & Premium Subscriptions**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-red.svg)](https://www.sqlalchemy.org/)
[![Paystack Integrated](https://img.shields.io/badge/Payments-Paystack-09A5DB.svg)](https://paystack.com/)
[![Architecture](https://img.shields.io/badge/Architecture-DDD--Lite%20%2B%20Orchestrator-orange.svg)]()

---

## 📖 Table of Contents
- [1. Project Overview & Current Status](#1-project-overview--current-status)
- [2. Architectural Pattern (DDD-Lite & Orchestrator)](#2-architectural-pattern-ddd-lite--orchestrator)
- [3. Strengths, Current Limitations & Evolution Roadmap](#3-strengths-current-limitations--evolution-roadmap)
- [4. Mobile Data Serialization Rules (Epoch Milliseconds)](#4-mobile-data-serialization-rules-epoch-milliseconds)
- [5. Complete API Contract & Integration Guide](#5-complete-api-contract--integration-guide)
  - [Authentication Domain (`/api/v1/auth`)](#-authentication-domain-apiv1auth)
  - [User Profile & Status Domain (`/api/v1/users`)](#-user-profile--status-domain-apiv1users)
  - [Payments & Paystack Webhook Domain (`/api/v1/payments`)](#-payments--paystack-webhook-domain-apiv1payments)
  - [Quotes & Offline Caching Domain (`/api/v1/quotes`)](#-quotes--offline-caching-domain-apiv1quotes)
- [6. Environment Setup & Execution Guide](#6-environment-setup--execution-guide)
- [7. Verification & Testing](#7-verification--testing)

---

## 1. Project Overview & Current Status

The **Ghana Motivation Backend** (powering the **Aquaba Mobile App**) is a modernized Python 3.10+ asynchronous backend migrated from legacy Express.js. It delivers daily motivational quotes based on UTC day-of-year, manages server-authoritative 3-day free trial periods, handles Paystack mobile money/card subscription payments, and provides batch caching endpoints for client-side local notification delivery.

### 🟡 Status: Beta MVP (Active Development / Production-Ready Core)
- **Engine:** Fully asynchronous (`asyncio` + `asyncpg` / `aiosqlite`).
- **Payment Processing:** Integrated with Paystack API + Dynamic Mock Client Mode for offline testing.
- **Security:** Double-hashed passwords (SHA-256 pre-hash + bcrypt) to bypass 72-byte limits + JWT Bearer token authentication.
- **Database:** Fully registered SQLAlchemy ORM models (`User`, `Payment`, `Subscription`, `Quote`).

---

## 2. Architectural Pattern (DDD-Lite & Orchestrator)

The project enforces **Domain-Driven Design Lite (DDD-Lite)** combined with the **Orchestrator Pattern**.

```
GhanaMotivationApp/
├── core/                  # Shared cross-cutting concerns (Enums, Security, Exception Hierarchy)
├── database/              # Async Engine, Session Factory, Base Model & Generic BaseRepository
├── settings/              # Pydantic Settings management (.env environment binding)
└── modules/               # Domain-Driven Modules
    ├── auth/              # Registration, Login, Token Issuance & Refresh
    ├── user/              # User Profile Management, Password Updates, Status Reconciliation
    ├── payment/           # Payment Initialization, Paystack Verification, HMAC Webhooks
    ├── paystack/          # HTTP Client Abstraction (Live REST API + Mock Mode)
    ├── quote/             # Daily Quotes, Random Quotes & Batch Offline Downloads
    └── subscription/      # Subscription Ledger & Expiry Extension Logic
```

### Layer Responsibilities:
1. **Routers (`router.py`):** Act strictly as HTTP entrypoints. Handle Pydantic request/response conversion and status codes.
2. **Services (`service.py`):** **Maestros / Orchestrators.** Contain pure domain logic, coordinate multiple repositories, and apply business rules (e.g. extending subscriptions from future expiry timestamps).
3. **Repositories (`repo.py`):** Data access specialists inheriting from `BaseRepository[Model]`. Execute raw SQLAlchemy queries.
4. **Schemas (`schemas.py` / `schema.py`):** Pydantic V2 schemas enforcing strict validation boundaries.

---

## 3. Strengths, Current Limitations & Evolution Roadmap

### 💚 Current Strengths
- **Server-Authoritative Trial & Premium Reconciliation:** Trial and premium statuses are re-calculated on the fly during `/users/status` calls, eliminating client-side clock tampering vulnerabilities.
- **Idempotent Payment Activations:** Payments double-check reference states to prevent duplicate activations, and auto-resolve user identity from Paystack customer payload if initialized externally.
- **Dynamic Mock Client Mode:** Allows end-to-end development and automated testing without real network calls or paid Paystack accounts.
- **Model Registry Safety:** `create_all_tables()` explicitly imports all models, preventing SQLAlchemy string-based relationship resolution crashes.

### 🟡 Current Limitations (Safe for Beta MVP)
- **Single Token Session Renewal:** `/auth/refresh` renews active access tokens. If a token has already expired, re-login is required. *(Mitigated by setting `ACCESS_TOKEN_EXPIRE_MINUTES=10080` / 7 days).*
- **SQLite Development Database:** Default configuration uses SQLite via `aiosqlite`. PostgreSQL configuration is provided and ready for production.

### 🚀 Future Evolution Roadmap (V2 Upgrade Path)
1. **Dual-Token System (V2):** Implement 15-minute `access_token` + 30-day server-blacklisted `refresh_token` stored in database.
2. **Alembic Database Migrations (V2):** Replace `create_all()` with Alembic versioned migration scripts.
3. **Redis Caching Layer (V2):** Cache daily quotes in Redis to reduce database read load under high concurrency.
4. **Google / Apple OAuth2 Single Sign-On (V2):** Add social authentication providers.

---

## 4. Mobile Data Serialization Rules (Epoch Milliseconds)

To maintain 100% API contract compatibility with the Flutter mobile application:

> ⚠️ **CRITICAL:** All datetime fields returned in JSON API responses are serialized as **Integer Unix Epoch Milliseconds** (not ISO 8601 strings).

**Example Pydantic Serializer:**
```json
{
  "trial_start": 1788214785232,
  "trial_end": 1788473985232,
  "premium_expires": null
}
```

---

## 5. Complete API Contract & Integration Guide

### 🛡️ Authentication Domain (`/api/v1/auth`)

#### 1. Register New User
- **Endpoint:** `POST /api/v1/auth/register`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
```json
{
  "name": "Kwame Mensah",
  "email": "kwame@example.com",
  "password": "SecurePassword123!",
  "device_fingerprint": "ANDROID_HW_ID_98765"
}
```
- **Response (`201 Created`):**
```json
{
  "id": 1,
  "email": "kwame@example.com",
  "name": "Kwame Mensah",
  "device_fingerprint": "ANDROID_HW_ID_98765",
  "trial_start": 1788214785232,
  "trial_end": 1788473985232,
  "is_premium": false,
  "premium_expires": null,
  "is_active": true,
  "created_at": 1788214785232,
  "updated_at": 1788214785232
}
```

#### 2. User Login
- **Endpoint:** `POST /api/v1/auth/login`
- **Headers:** `Content-Type: application/json` or `application/x-www-form-urlencoded`
- **Request Body:**
```json
{
  "email": "kwame@example.com",
  "password": "SecurePassword123!"
}
```
- **Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...",
  "token_type": "bearer"
}
```

#### 3. Refresh Token Session
- **Endpoint:** `POST /api/v1/auth/refresh`
- **Headers:** `Authorization: Bearer <valid_access_token>`
- **Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...",
  "token_type": "bearer"
}
```

---

### 👤 User Profile & Status Domain (`/api/v1/users`)

#### 1. Get Authenticated User Profile
- **Endpoint:** `GET /api/v1/users/me`
- **Headers:** `Authorization: Bearer <access_token>`
- **Response (`200 OK`):**
```json
{
  "id": 1,
  "email": "kwame@example.com",
  "name": "Kwame Mensah",
  "device_fingerprint": "ANDROID_HW_ID_98765",
  "trial_start": 1788214785232,
  "trial_end": 1788473985232,
  "is_premium": false,
  "premium_expires": null,
  "is_active": true,
  "created_at": 1788214785232,
  "updated_at": 1788214785232
}
```

#### 2. Get Subscription & Trial Status
- **Endpoint:** `GET /api/v1/users/status`
- **Headers:** `Authorization: Bearer <access_token>`
- **Response (`200 OK`):**
```json
{
  "user": {
    "id": 1,
    "email": "kwame@example.com",
    "name": "Kwame Mensah",
    "device_fingerprint": "ANDROID_HW_ID_98765",
    "trial_start": 1788214785232,
    "trial_end": 1788473985232,
    "is_premium": false,
    "premium_expires": null,
    "is_active": true,
    "created_at": 1788214785232,
    "updated_at": 1788214785232
  },
  "trial_remaining_seconds": 259200,
  "is_premium": false,
  "is_trial_active": true,
  "premium_expires": null
}
```

#### 3. Change Password
- **Endpoint:** `PATCH /api/v1/users/me/password`
- **Headers:** `Authorization: Bearer <access_token>`
- **Request Body:**
```json
{
  "old_password": "SecurePassword123!",
  "new_password": "NewSuperPassword456!"
}
```
- **Response (`200 OK`):** User profile object.

---

### 💳 Payments & Paystack Webhook Domain (`/api/v1/payments`)

#### 1. Initialize Paystack Subscription Payment
- **Endpoint:** `POST /api/v1/payments/initialize`
- **Request Body:**
```json
{
  "user_id": 1,
  "email": "kwame@example.com",
  "amount": 1000
}
```
- **Response (`200 OK`):**
```json
{
  "authorization_url": "https://checkout.paystack.com/mock/MOCK-A1B2C3D4E5F6",
  "reference": "MOCK-A1B2C3D4E5F6"
}
```

#### 2. Verify Payment Transaction
- **Endpoint:** `GET /api/v1/payments/verify?reference=MOCK-A1B2C3D4E5F6`
- **Response (`200 OK`):**
```json
{
  "id": 1,
  "reference": "MOCK-A1B2C3D4E5F6",
  "amount": 1000,
  "currency": "GHS",
  "status": "success",
  "paid_at": 1788214800000,
  "user_id": 1,
  "created_at": 1788214785232,
  "updated_at": 1788214800000
}
```

#### 3. Paystack Webhook Event Listener
- **Endpoint:** `POST /api/v1/payments/webhook`
- **Headers:** `X-Paystack-Signature: <hmac_sha512_hash>`
- **Raw Body:** Paystack event JSON bytes.
- **Response (`200 OK`):** `{"status": "ok"}`

---

### 💡 Quotes & Offline Caching Domain (`/api/v1/quotes`)

#### 1. Get Today's Quote
- **Endpoint:** `GET /api/v1/quotes/today`
- **Response (`200 OK`):**
```json
{
  "id": 1,
  "day_number": 244,
  "content": "Do not wait to strike till the iron is hot; but make it hot by striking.",
  "author": "William Butler Yeats",
  "category": "Perseverance"
}
```

#### 2. Get Random Quote
- **Endpoint:** `GET /api/v1/quotes/random`
- **Response (`200 OK`):** Quote object.

#### 3. Get Batch Quotes for Offline Mobile Caching
- **Endpoint:** `GET /api/v1/quotes/batch?start_day=1&end_day=7`
- **Response (`200 OK`):** Array of quote objects for day numbers 1 through 7.

---

## 6. Environment Setup & Execution Guide

### Prerequisites
- **Python:** `3.10+`
- **Virtual Environment:** `venv` or `uv`

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd ghana-motivation-backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r pyproject.toml
   # Or using uv:
   uv pip install -e .
   ```

4. **Environment Variables (`.env` file):**
   Create a `.env` file in the root directory:
   ```env
   HOST=127.0.0.1
   PORT=8000
   RELOAD=True
   API_PREFIX=/api/v1

   DATABASE_URL=sqlite+aiosqlite:///./test.db
   ECHO=False

   SECRET_KEY=your-super-secret-jwt-signing-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=10080

   PAYSTACK_SECRET_KEY=sk_test_your_paystack_secret_key
   PAYSTACK_PUBLIC_KEY=pk_test_your_paystack_public_key
   PAYSTACK_MODE=mock

   TRIAL_DAYS=3
   SUBSCRIPTION_DAYS=30
   SUBSCRIPTION_AMOUNT_PESEWAS=1000
   ```

5. **Run the ASGI Development Server:**
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

6. **Interactive OpenAPI Documentation:**
   Open your browser to:
   - **Swagger UI:** `http://127.0.0.1:8000/docs`
   - **ReDoc:** `http://127.0.0.1:8000/redoc`

---

## 7. Verification & Testing

To run automated end-to-end verification tests:

```bash
.\.venv\Scripts\python.exe -c "
import asyncio
from GhanaMotivationApp.database.session import AsyncSessionLocal
from GhanaMotivationApp.modules.auth.schemas import RegisterRequest, LoginRequest
from GhanaMotivationApp.modules.auth.service import register_user, login_user

async def verify():
    async with AsyncSessionLocal() as session:
        login_req = LoginRequest(email='kwame@example.com', password='SecurePassword123!')
        token = await login_user(login_req, session)
        print('✅ System Operational! Token issued successfully:', token.access_token[:25] + '...')

asyncio.run(verify())
"
```

---
*Built with ❤️ by Google DeepMind Team for Aquaba Motivation Backend.*
