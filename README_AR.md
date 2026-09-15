# 🇬🇭 البنية التحتية الخلفية لتطبيق تحفيز غانا — Aquaba Enterprise Infrastructure

> **محرك واجهة برمجة تطبيقات (RESTful API) عالي الأداء وغير متزامن (Asynchronous) لتقديم الاقتباسات اليومية، المزامنة دون اتصال للهواتف المحمولة، والاشتراكات المالية الصفرية الثقة عبر Paystack.**

[![إصدار بايثون](https://img.shields.io/badge/Python-3.10%2B%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![إطار العمل FastAPI](https://img.shields.io/badge/Framework-FastAPI%200.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![التحقق Pydantic](https://img.shields.io/badge/Validation-Pydantic%20V2-e92063.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![محرك قواعد البيانات SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0%20Async-d71f00.svg?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![قاعدة البيانات](https://img.shields.io/badge/Database-SQLite%20(aiosqlite)%20%7C%20PostgreSQL%20(asyncpg)-4169e1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![الأمان والتشفير](https://img.shields.io/badge/Hashing-Argon2id%20%2B%20JWT%20Rotation-black.svg?logo=auth0&logoColor=white)](https://argon2-cffi.readthedocs.io/)
[![بوابة الدفع](https://img.shields.io/badge/Payments-Paystack%20%28Mobile%20Money%20%2B%20Cards%29-09A5DB.svg?logo=paystack&logoColor=white)](https://paystack.com/)
[![حزمة الاختبارات](https://img.shields.io/badge/Tests-100%25%20Passed%20(Dual--Transport)-brightgreen.svg?logo=checkmarx&logoColor=white)](./tests/)
[![المعمارية البرمجية](https://img.shields.io/badge/Architecture-DDD--Lite%20%7C%20Orchestrator%20Pattern-orange.svg)]()

---

## 📑 فهرس المحتويات
- [1. الملخص التنفيذي ورؤية المشروع](#1-الملخص-التنفيذي-ورؤية-المشروع)
- [2. المعمارية البرمجية وفلسفة التصميم](#2-المعمارية-البرمجية-وفلسفة-التصميم)
- [3. القدرات المؤسسية والتحصينات الأمنية](#3-القدرات-المؤسسية-والتحصينات-الأمنية)
- [4. حزمة التقنيات المستخدمة (Tech Stack)](#4-حزمة-التقنيات-المستخدمة-tech-stack)
- [5. الهيكل التنظيمي للمشروع ومسارات الملفات](#5-الهيكل-التنظيمي-للمشروع-ومسارات-الملفات)
- [6. المخطط الهيكلي لقاعدة البيانات ونماذج البيانات](#6-المخطط-الهيكلي-لقاعدة-البيانات-ونماذج-البيانات)
- [7. الدليل المرجعي الشامل لنقاط النهاية (API Endpoints Catalog)](#7-الدليل-المرجعي-الشامل-لنقاط-النهاية-api-endpoints-catalog)
  - [نطاق المصادقة والجلسات (`/api/v1/auth`)](#-نطاق-المصادقة-والجلسات-apiv1auth)
  - [نطاق الملف الشخصي والاشتراك (`/api/v1/users`)](#-نطاق-الملف-الشخصي-والاشتراك-apiv1users)
  - [نطاق المدفوعات والـ Webhooks بحدود الصفرية الثقة (`/api/v1/payments`)](#-نطاق-المدفوعات-والـ-webhooks-بحدود-الصفرية-الثقة-apiv1payments)
  - [نطاق الاقتباسات والمزامنة دون اتصال (`/api/v1/quotes`)](#-نطاق-الاقتباسات-والمزامنة-دون-اتصال-apiv1quotes)
- [8. معيار تسلسل البيانات لتطبيقات الهواتف المحمولة (Epoch Milliseconds)](#8-معيار-تسلسل-البيانات-لتطبيقات-الهواتف-المحمولة-epoch-milliseconds)
- [9. ضبط وتكوين متغيرات البيئة (`.env`)](#9-ضبط-وتكوين-متغيرات-البيئة-env)
- [10. التشغيل السريع والتهيئة المحلية](#10-التشغيل-السريع-والتهيئة-المحلية)
- [11. حزمة الاختبارات الشاملة المعتمدة (`tests/`)](#11-حزمة-الاختبارات-الشاملة-المعتمدة-tests)
- [12. النشر والإنتاج والتحصين المؤسسي (Production Deployment)](#12-النشر-والإنتاج-والتحصين-المؤسسي-production-deployment)
- [13. دليل معالجة الأخطاء والأسئلة الشائعة (FAQ)](#13-دليل-معالجة-الأخطاء-والأسئلة-الشائعة-faq)
- [14. الحوكمة المعمارية والترخيص](#14-الحوكمة-المعمارية-والترخيص)

---

## 1. الملخص التنفيذي ورؤية المشروع

يُمثل مشروع **Ghana Motivation Backend** النواة الخلفية الحساسة التي تُشغل تطبيق الهواتف المحمولة **Aquaba App** الموجه لجمهورية غانا ودول غرب إفريقيا. يقوم النظام بتقديم جرعات يومية ملهمة من الاقتباسات، إدارة فترة تجريبية مجانية مدتها 3 أيام تُحسب مركزياً على السيرفر، معالجة اشتراكات الهاتف المحمول (MTN Mobile Money و Vodafone Cash والبطاقات البنكية) عبر منصة **Paystack** المالية، وتوفير نقاط نهاية للتحميل المجمّع لتمكين الهواتف من جدولة الإشعارات والعمل الكامل دون الحاجة لاتصال بالإنترنت.

تمت هندسة هذا النظام بالكامل استناداً إلى لغة **Python 3.10+** وإطار العمل **FastAPI** وفقاً لأعلى معايير المؤسسات الكبرى: معالجة غير متزامنة بالكامل (100% Async/Await)، استخدام خوارزمية التشفير العالمية **Argon2id** لتأمين كلمات المرور، نظام تدوير التوكنات المزدوج (JWT Rotation) مع الكشف الفوري لسرقة الجلسات، وحدود أمان مالي صفرية الثقة تمنع أي تلاعب خارجي بالأسعار أو المعاملات.

---

## 2. المعمارية البرمجية وفلسفة التصميم

يتبع المشروع بدقة نمط **Domain-Driven Design Lite (DDD-Lite)** بالتكامل مع نمط **Orchestrator Pattern** ودستور هندسة بايثون المتقدمة (**Enterprise Python Architecture Constitution**).

```mermaid
graph TD
    Client[تطبيق الهاتف المحمول / المتصفح] -->|HTTP / JSON| Router[طبقة التوجيه FastAPI Routers]
    Router -->|التحقق من البيانات عبر Pydantic V2| Service[طبقة الخدمات - المنسق Orchestrator]
    Service -->|منطق العمل والتنسيق| Repo[طبقة المستودعات - المتخصصين Specialists]
    Service -->|استدعاءات HTTP| PaystackClient[عميل بوابة Paystack المجرّد]
    Repo -->|SQLAlchemy 2.0 Async| DB[(قاعدة البيانات غير المتزامنة - SQLite / PostgreSQL)]
    Service -->|أدوات الأمان والتشفير| CoreSecurity[محرك التشفير Argon2id و JWT]
```

### مسؤوليات الطبقات المعمارية:
1. **الواجهات الخارجية (`__init__.py` - Facade Pattern):** يُعرّف كل مجلد واجهته البرمجية العامة حصرياً عبر التوبل `__all__`، لمنع التلوث النطاقي وتفادي مشاكل الاستيراد الدائري نهائياً.
2. **الموجّهات (`router.py`):** نقاط وصول الـ HTTP التي تقتصر مسؤوليتها على حقن التبعيات (Dependency Injection)، استلام الطلبات، التحقق من المخططات، وإرجاع رموز الحالة الصحيحة. يُمنع كتابة أي استعلامات قواعد بيانات أو حسابات منطقية داخلها.
3. **الخدمات (`service.py` - Orchestrators):** "المايسترو" الذي يقود تدفق العمليات، ينسق بين المستودعات المختلفة، يطبق الشروط الحسابية والمالية (مثل تمديد الاشتراكات وتدوير الجلسات)، ويصدر نماذج بيانات محكمة النوع.
4. **المستودعات (`repo.py` - Specialists):** طبقة الوصول إلى البيانات الملتزمة بمبدأ المسؤولية الفردية (SRP)، وترث من `BaseRepository[T]` لتنفيذ استعلامات SQL غير المتزامنة عبر SQLAlchemy 2.0.
5. **المخططات (`schema.py`):** نماذج Pydantic V2 التي تحمي حدود النظام وتفرض التحقق الصارم من المدخلات والمخرجات، مع تطبيق معيار التسلسل الزمني بالملي ثانية.
6. **النواة المشتركة (`GhanaMotivationApp/core/`):** تحتوي على الأدوات العابرة للنطاقات كالتشفير، شجرة الاستثناءات الموحدة، والقوائم الثابتة المحدودة (Enums).

---

## 3. القدرات المؤسسية والتحصينات الأمنية

### 🛡️ 1. المصادقة المتقدمة ودرع الحماية من سرقة الجلسات (Theft Guard)
- **تشفير كلمات المرور بـ Argon2id:** استخدام مكتبة `argon2-cffi` الموصى بها عالمياً لمقاومة هجمات الـ GPU و ASIC وجداول Rainbow Tables.
- **دورة حياة التوكنات المزدوجة:** رمز وصول قصير الأجل (`access_token` لمدة 30 دقيقة) بالتزامن مع رمز تجديد طويل الأجل مسجل بقاعدة البيانات (`refresh_token` لمدة 30 يوماً).
- **تدوير التوكنات التلقائي (Token Rotation):** كل عملية تجديد تؤدي لإلغاء الرمز القديم وإصدار زوج جديد كلياً.
- **كشف وإحباط سرقة الجلسات (Token Reuse Detection):** في حال قام مهاجم بمحاولة استخدام رمز تجديد مستهلك، يكتشف النظام فوراً حدوث اختراق ويلغي سلسلة الجلسة بالكامل من قاعدة البيانات (`401 Unauthorized`).
- **تسجيل الخروج المرن:** إمكانية إلغاء جلسة الجهاز الحالي فقط (`/auth/logout`)، أو إلغاء كافة جلسات المستخدم من جميع أجهزته بنقرة واحدة (`/auth/logout-all`).

### ⏱️ 2. احتساب الفترات التجريبية والاشتراكات بسلطة السيرفر المطلقة
- **حسابات غير قابلة للتلاعب:** تُحسب الفترات التجريبية (3 أيام) وصلاحية الاشتراكات لحظياً في السيرفر بناءً على توقيت UTC الثابت، مما يُبطل محاولات التلاعب بساعة الهاتف لفتح المحتوى مجاناً.
- **التمديد التراكمي العادل للاشتراكات:** عند قيام المستخدم بتجديد اشتراكه قبل انتهاء مدته، تُضاف الـ 30 يوماً إلى *تاريخ الانتهاء المستقبلي* بدلاً من التصفير من اللحظة الراهنة، حفاظاً على أيام المشترك المدفوعة.

### 💳 3. حدود الأمان المالي الصفرية الثقة (Zero-Trust Paystack Boundaries)
- **انعدام الثقة في تسعير العميل:** لا يستطيع تطبيق العميل إرسال قيمة المبلغ المالي؛ بل يقوم السيرفر بفرض السعر المعتمد حصرياً من إعدادات النظام الداخلية (`SUBSCRIPTION_PRICE_GHS`).
- **حماية ملكية المعاملات (Ownership Guard):** استحالة قيام مستخدم بفحص أو تفعيل معاملة دفع تخص مستخدماً آخر (ممنوع برمز `403 Forbidden`).
- **التحقق المشفر من إشعارات Paystack (Webhooks):** فحص ترويسة `X-Paystack-Signature` ومطابقتها مع توقيع HMAC-SHA512 المشفر بالمفتاح السري. يتم طرد أي طلب مزور فوراً بكود `401 Unauthorized`.
- **معيار عدم التكرار (Idempotency):** لا يؤدي تكرار وصول إشعارات الـ Webhook أو إعادة استدعاء الفحص إلى تكرار تفعيل الاشتراكات أو تشويه سجلات الحساب.

### 📴 4. المزامنة المجمعة دون اتصال للهواتف المحمولة (Offline Batch Sync)
- **تحميل الحزم المتسلسلة:** تتيح للتطبيق تنزيل نطاق مخصص من الاقتباسات (مثل الأيام من 1 إلى 30، أو السنة كاملة 365 يوماً) لتخزينها محلياً وجدولة إشعارات الهاتف حتى في أوقات انقطاع شبكة الهاتف.
- **معالجة السنوات الكبيسة (Leap Year):** يتم توجيه اليوم 366 تلقائياً وبأمان إلى اليوم 365 لمنع أي استثناءات في قاعدة البيانات.

---

## 4. حزمة التقنيات المستخدمة (Tech Stack)

| المكوّن التقني | التقنية المستخدمة | الإصدار | الوظيفة الهندسية |
|---|---|---|---|
| **بيئة التشغيل** | Python | `3.10+` (تم الفحص على `3.13`) | لغة البرمجة الأساسية مع دعم PEP 695 typing |
| **إطار عمل الويب** | FastAPI | `0.115.0+` | إطار عمل الـ REST API غير المتزامن فائق السرعة |
| **خادم ASGI** | Uvicorn | `0.30.0+` | خادم ويب قياسي لمعالجة آلاف الطلبات المتزامنة |
| **التحقق من البيانات** | Pydantic V2 | `2.9.0+` | فحص وتدقيق حدود البيانات وتسلسل الملي ثانية |
| **إدارة الإعدادات** | Pydantic Settings | `2.5.0+` | إدارة متغيرات البيئة وفق منهجية Twelve-Factor |
| **محرك قواعد البيانات** | SQLAlchemy | `2.0.35+` | أداة الربط العلائقي غير المتزامنة (Async ORM) |
| **برامج تشغيل البيانات** | aiosqlite / asyncpg | أحدث إصدار | موصلات قواعد البيانات غير المتزامنة لـ SQLite و PostgreSQL |
| **تشفير كلمات المرور** | Argon2id (`argon2-cffi`)| `23.1.0+` | خوارزمية التشفير الفائزة بمسابقة PHC المقاومة للعتاد العالي |
| **إدارة التوكنات** | PyJWT | `2.9.0+` | توليد وفك تشفير الرموز الموقعة رقمياً (HS256) |
| **عميل الـ HTTP** | HTTPX | `0.27.0+` | عميل غير متزامن للتواصل مع Paystack وتنفيذ الاختبارات |

---

## 5. الهيكل التنظيمي للمشروع ومسارات الملفات

```text
ghana-motivation-backend/
├── GhanaMotivationApp/             # الحزمة البرمجية الأساسية
│   ├── core/                       # الأدوات الأساسية والبنية المشتركة
│   │   ├── __init__.py             # الواجهة الخارجية Facade
│   │   ├── enums.py                # الحالات المحدودة (EnvironmentEnum, CurrencyEnum, إلخ)
│   │   ├── exceptions.py           # شجرة الاستثناءات المخصصة والموحدة
│   │   └── security.py            # محرك تشفير Argon2id وإدارة JWT
│   ├── database/                   # البنية التحتية لقاعدة البيانات غير المتزامنة
│   │   ├── __init__.py             # الواجهة الخارجية Facade
│   │   ├── base.py                 # الأساس التعريفي والـ AuditMixin لتواريخ الإنشاء والتعديل
│   │   ├── repo.py                 # مستودع البيانات العام Generic BaseRepository[T]
│   │   └── session.py              # محرك الاتصال غير المتزامن ومصنع الجلسات
│   ├── settings/                   # الإعدادات المركزية
│   │   ├── __init__.py             # تصدير كائن الإعدادات settings
│   │   └── s.py                    # نموذج إعدادات Pydantic Settings مع مدققات الإنتاج
│   └── modules/                    # الوحدات الوظيفية المفصولة حسب النطاق (DDD Modules)
│       ├── auth/                   # التسجيل، الدخول، تدوير التوكنات، وتسجيل الخروج
│       ├── user/                   # إدارة الملف الشخصي، تغيير كلمة المرور، وحالة الاشتراك
│       ├── payment/                # المدفوعات، بوابة Paystack، والـ Webhooks
│       ├── paystack/               # عميل الاتصال بـ Paystack ونمط المحاكاة (Mock Client)
│       ├── quote/                  # اقتباس اليوم، الاقتباس العشوائي، والتحميل المجمّع
│       └── subscription/           # سجل الاشتراكات وإدارة مدة التجديد
├── scripts/                        # سكربتات الصيانة والإدارة والتهيئة
│   ├── seed_quotes.py              # بذر 365 اقتباساً تحفيزياً منتقى في قاعدة البيانات
│   └── seed_users.py               # بذر مستخدمين تجريبيين للتطوير
├── tests/                          # حزمة الاختبارات التكاملية الشاملة
│   ├── __init__.py                 # تصدير دوال الفحص والعميل
│   ├── config.py                   # محرك النقل الذكي المزدوج (Dual-Transport) وطباعة النتائج
│   ├── run_all_tests.py            # منسق الاختبارات الشامل الموحّد (Master Runner)
│   ├── test_01_auth.py             # فحص نطاق المصادقة والجلسات
│   ├── test_02_users.py            # فحص نطاق المستخدمين والأمان
│   ├── test_03_payments.py         # فحص نطاق المدفوعات والـ Webhook
│   ├── test_04_quotes.py           # فحص نطاق الاقتباسات والمزامنة دون اتصال
│   └── README.md                   # الدليل التشغيلي لحزمة الاختبارات
├── main.py                         # نقطة البداية، مصنع التطبيق، ودورة حياة السيرفر (Lifespan)
├── requirements.txt                # قائمة الاعتماديات والمكتبات المطلوبة
├── pyproject.toml                  # بيانات الحزمة الحديثة وإعدادات الأدوات
├── README.md                       # دليل المشروع الشامل باللغة الإنجليزية
└── README_AR.md                    # دليل المشروع الشامل باللغة العربية (هذا الملف)
```

---

## 6. المخطط الهيكلي لقاعدة البيانات ونماذج البيانات

```mermaid
erDiagram
    USERS ||--o{ REFRESH_TOKENS : يمتلك
    USERS ||--o{ PAYMENTS : ينشئ
    USERS ||--o{ SUBSCRIPTIONS : يملك

    USERS {
        int id PK "المعرف الأساسي"
        string email UK "البريد الإلكتروني الفريد"
        string name "الاسم الكامل"
        string hashed_password "تجزئة كلمة المرور Argon2id"
        string device_fingerprint "بصمة عتاد جهاز الهاتف"
        datetime trial_start "بداية الفترة التجريبية"
        datetime trial_end "نهاية الفترة التجريبية"
        boolean is_premium "هل الحساب مميز مدفوع"
        datetime premium_expires "تاريخ انتهاء الاشتراك المميز"
        boolean is_active "هل الحساب مفعل"
        datetime created_at "تاريخ الإنشاء"
        datetime updated_at "تاريخ التحديث"
    }

    REFRESH_TOKENS {
        int id PK "معرف الرمز"
        string token UK "قيمة التوكن الفريدة"
        int user_id FK "معرف المستخدم المرتبط"
        datetime expires_at "تاريخ انتهاء الصلاحية"
        boolean is_revoked "هل تم إلغاء الرمز"
        datetime created_at "تاريخ الإصدار"
    }

    PAYMENTS {
        int id PK "معرف المعاملة"
        string reference UK "مرجع Paystack الفريد"
        int amount "المبلغ بالبيسيوا Pesewas"
        string currency "العملة (GHS)"
        string status "حالة الدفع (success, pending)"
        datetime paid_at "تاريخ الدفع الفعلي"
        int user_id FK "المستخدم صاحب المعاملة"
        datetime created_at "تاريخ الإنشاء"
        datetime updated_at "تاريخ التحديث"
    }

    SUBSCRIPTIONS {
        int id PK "معرف الاشتراك"
        int user_id FK "معرف المشترك"
        datetime start_date "تاريخ بداية الاشتراك"
        datetime next_billing "تاريخ التجديد القادم"
        string status "حالة الاشتراك (active, expired)"
        datetime created_at "تاريخ التسجيل"
        datetime updated_at "تاريخ التعديل"
    }

    QUOTES {
        int id PK "معرف الاقتباس"
        int day_number UK "رقم اليوم من السنة (1-365)"
        string content "نص الاقتباس التحفيزي"
        string author "اسم القائل"
        string category "التصنيف"
        boolean is_active "هل الاقتباس نشط"
        datetime created_at "تاريخ الإنشاء"
        datetime updated_at "تاريخ التحديث"
    }
```

---

## 7. الدليل المرجعي الشامل لنقاط النهاية (API Endpoints Catalog)

كافة نقاط النهاية تبدأ بالبادئة `/api/v1`. التوثيق التفاعلي متاح عبر `/docs` (Swagger UI) و `/redoc`.

### 🛡️ نطاق المصادقة والجلسات (`/api/v1/auth`)

| الطريقة | المسار | الوصف | المصادقة المطلوبة | رموز الاستجابة |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | تسجيل مستخدم جديد وبدء الفترة التجريبية (3 أيام) | لا يوجد | `201`, `409`, `422` |
| `POST` | `/api/v1/auth/login` | مصادقة بيانات الدخول وإصدار زوج التوكنات المزدوج | لا يوجد | `200`, `401`, `422` |
| `POST` | `/api/v1/auth/refresh` | تدوير رمز التجديد، كشف التوكنات المسروقة، وإصدار توكن جديد | لا يوجد (عبر الـ Body) | `200`, `401`, `422` |
| `POST` | `/api/v1/auth/logout` | إلغاء جلسة الجهاز الحالي وإبطال رمز التجديد | Bearer JWT | `200`, `401`, `422` |
| `POST` | `/api/v1/auth/logout-all` | تسجيل الخروج الجماعي وإلغاء كافة جلسات المستخدم من كل الأجهزة | Bearer JWT | `200`, `401` |

#### مثال طلب التسجيل (Register Request):
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

#### مثال طلب تسجيل الدخول (Login Request):
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "kwame@example.com",
    "password": "SecurePassword123!"
  }'
```

---

### 👤 نطاق الملف الشخصي والاشتراك (`/api/v1/users`)

| الطريقة | المسار | الوصف | المصادقة المطلوبة | رموز الاستجابة |
|---|---|---|---|---|
| `GET` | `/api/v1/users/me` | جلب الملف الشخصي للمستخدم المصادق عليه حالياً | Bearer JWT | `200`, `401` |
| `GET` | `/api/v1/users/status` | الحساب اللحظي لحالة التجربة المجانية والاشتراك المميز | Bearer JWT | `200`, `401` |
| `PATCH`| `/api/v1/users/me/password` | التحقق من كلمة المرور القديمة وتدويرها لتجزئة جديدة | Bearer JWT | `200`, `401`, `422` |

#### مثال استجابة حالة المستخدم (User Status Response):
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

### 💳 نطاق المدفوعات والـ Webhooks بحدود الصفرية الثقة (`/api/v1/payments`)

| الطريقة | المسار | الوصف | المصادقة المطلوبة | رموز الاستجابة |
|---|---|---|---|---|
| `POST` | `/api/v1/payments/initialize` | تهيئة جلسة دفع Paystack بالسعر الرسمي المعتمد من السيرفر | Bearer JWT | `200`, `401` |
| `GET` | `/api/v1/payments/verify` | فحص مرجع الدفع وتفعيل الاشتراك المميز 30 يوماً بأمان وتكرار آمن | Bearer JWT | `200`, `401`, `403`, `404` |
| `POST` | `/api/v1/payments/webhook` | استقبال إشعارات Paystack غير المتزامنة والتحقق من توقيع HMAC | ترويسة التوقيع | `200`, `401` |

#### طلب تهيئة الدفع:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/initialize" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"payment_method": "mobile_money"}'
```

#### الاستجابة:
```json
{
  "authorization_url": "https://checkout.paystack.com/mock/MOCK-A1B2C3D4E5F6",
  "reference": "MOCK-A1B2C3D4E5F6"
}
```

---

### 💡 نطاق الاقتباسات والمزامنة دون اتصال (`/api/v1/quotes`)

| الطريقة | المسار | الوصف | المصادقة المطلوبة | رموز الاستجابة |
|---|---|---|---|---|
| `GET` | `/api/v1/quotes/today` | جلب اقتباس اليوم المتوافق مع رقم اليوم الحالي من السنة (UTC) | لا يوجد | `200`, `404` |
| `GET` | `/api/v1/quotes/random` | جلب اقتباس عشوائي نشط | لا يوجد | `200`, `404` |
| `GET` | `/api/v1/quotes/batch` | استعلام نطاق الأيام (`start_day` إلى `end_day`) للمزامنة في الهاتف | لا يوجد | `200`, `422` |

#### مثال تحميل دفعة أسبوعية (الأيام من 1 إلى 7):
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/quotes/batch?start_day=1&end_day=7"
```

---

## 8. معيار تسلسل البيانات لتطبيقات الهواتف المحمولة (Epoch Milliseconds)

لضمان التوافق التام وغير القابل للكسر مع تطبيقات Flutter/Dart على أجهزة Android و iOS:

> ⚠️ **معيار معماري صارم:** كافة الحقول الزمنية والتواريخ (`created_at`, `updated_at`, `trial_start`, `trial_end`, `premium_expires`, `paid_at`) يتم تحويلها وإرسالها في الاستجابات كـ **أرقام صحيحة بالملي ثانية منذ بداية العصر الرقمي (Integer Unix Epoch Milliseconds)** (مثال: `1788214785232`)، و**يُمنع منعاً باتاً** إرسالها كسلاسل نصوص ISO 8601.

هذا المعيار يمنع أخطاء تحويل المناطق الزمنية (Timezones) في أجهزة الهواتف المحمولة المختلفة.

---

## 9. ضبط وتكوين متغيرات البيئة (`.env`)

يتم تحميل وإدارة كافة الإعدادات عبر مكتبة `pydantic-settings`. يمكن إنشاء ملف `.env` في جذر المشروع يحتوي على المتغيرات التالية:

| المتغير | النوع | القيمة الافتراضية | الوصف التفصيلي |
|---|---|---|---|
| `ENVIRONMENT` | `str` | `development` | بيئة التشغيل (`development`, `staging`, `production`). في بيئة الإنتاج يتم إيقاف السيرفر فوراً إذا كانت المفاتيح الافتراضية مستخدمة. |
| `HOST` | `str` | `127.0.0.1` | عنوان واجهة الشبكة التي يرتبط بها خادم Uvicorn. |
| `PORT` | `int` | `8000` | رقم منفذ الاستماع TCP. |
| `RELOAD` | `bool` | `False` | إعادة تشغيل الخادم تلقائياً عند تعديل الملفات (خاص بالتطوير فقط). |
| `API_PREFIX` | `str` | `/api/v1` | البادئة العامة لكافة نقاط النهاية. |
| `DATABASE_URL` | `str` | `sqlite+aiosqlite:///./test.db` | رابط الاتصال غير المتزامن بقاعدة البيانات. في الإنتاج استخدم: `postgresql+asyncpg://user:pass@host/db`. |
| `ECHO` | `bool` | `False` | تفعيل تسجيل كافة استعلامات SQL في سطر الأوامر. |
| `SECRET_KEY` | `str` | `*مطلوب في الإنتاج*` | المفتاح السري لتوقيع توكنات الوصول (Access Tokens). |
| `REFRESH_SECRET_KEY`| `str` | `*مطلوب في الإنتاج*` | مفتاح سري منفصل لتوقيع توكنات التجديد (Refresh Tokens). |
| `ALGORITHM` | `str` | `HS256` | خوارزمية التوقيع الرقمي للتوكنات. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | `30` | صلاحية توكن الوصول بالدقائق. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `int` | `30` | صلاحية توكن التجديد بالأيام. |
| `PAYSTACK_SECRET_KEY` | `str` | `*مطلوب في الإنتاج*` | المفتاح السري المستخرج من لوحة تحكم Paystack. |
| `PAYSTACK_PUBLIC_KEY` | `str` | `*مطلوب في الإنتاج*` | المفتاح العام المستخرج من لوحة تحكم Paystack. |
| `PAYSTACK_MODE` | `str` | `mock` | نمط الاتصال: `mock` (محاكاة محلية دون إنترنت) أو `live`. |
| `TRIAL_DAYS` | `int` | `3` | مدة الفترة التجريبية المجانية بالأيام. |
| `SUBSCRIPTION_DAYS` | `int` | `30` | مدة دورة الاشتراك المدفوع بالأيام. |
| `SUBSCRIPTION_AMOUNT_PESEWAS` | `int` | `1000` | السعر المعتمد للاشتراك بالبيسيوا الغاني (1000 بيسيوا = 10 سيدي غاني GHS). |

---

## 10. التشغيل السريع والتهيئة المحلية

### 1. المتطلبات الأساسية
- تثبيت لغة بايثون بإصدار `3.10` أو أحدث (يُفضل `3.11` إلى `3.13`).
- توفر أداة Git على جهازك.

### 2. تجهيز البيئة الافتراضية
```powershell
# 1. استنساخ المستودع
git clone <repository-url>
cd ghana-motivation-backend

# 2. إنشاء وتفعيل البيئة الافتراضية
python -m venv .venv

# على نظام Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# على نظام Linux / macOS:
source .venv/bin/activate

# 3. تحديث أداة pip وتثبيت مكتبات المشروع
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. تهيئة قاعدة البيانات وبذر الاقتباسات
قبل تشغيل السيرفر، قم بتهيئة قاعدة البيانات وبذر الاقتباسات الـ 365:
```powershell
python scripts/seed_quotes.py
```

### 4. تشغيل السيرفر للتطوير
```powershell
python main.py
# أو تشغيله مباشرة عبر Uvicorn:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
افتح المتصفح وتوجه إلى الرابط التفاعلي: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## 11. حزمة الاختبارات الشاملة المعتمدة (`tests/`)

يحتوي المشروع على بيئة اختبارات متكاملة في المجلد `tests/` تعمل باستراتيجية النقل المزدوج الذكي (**Smart Dual-Transport Strategy**):
1. **نمط السيرفر المباشر (Live HTTP Mode):** يتصل تلقائياً بالسيرفر عبر المنفذ `8000` إذا كان يعمل في نافذة أخرى.
2. **نمط المحاكاة الداخلية (In-Memory ASGI Fallback Mode):** إذا لم يكن السيرفر يعمل، تُنفذ الاختبارات في الذاكرة عبر `httpx.ASGITransport` بسرعة وموثوقية فائقة.

### تشغيل الفحص الشامل الموحّد (Master Test Pipeline)
```powershell
python tests/run_all_tests.py
```

### تشغيل فحص نطاق معين بمفرده
```powershell
# المصادقة والجلسات
python tests/test_01_auth.py

# المستخدمين وتغيير كلمات المرور
python tests/test_02_users.py

# المدفوعات والـ Webhooks
python tests/test_03_payments.py

# الاقتباسات والمزامنة دون اتصال
python tests/test_04_quotes.py
```

للحصول على دليل التشخيص الكامل، راجع [دليل الاختبارات: tests/README.md](file:///d:/_Python%20Projects-27-05-2026/ghana-motivation-backend/tests/README.md).

---

## 12. النشر والإنتاج والتحصين المؤسسي (Production Deployment)

عند رفع المشروع إلى بيئات الاختبار المتقدمة (Staging) والإنتاج الفعلي (Production):
1. **التحويل إلى قاعدة بيانات PostgreSQL:**
   ```env
   DATABASE_URL=postgresql+asyncpg://db_user:db_password@db-host:5432/ghana_motivation_prod
   ```
2. **تفعيل نمط الإنتاج الصارم:**
   ```env
   ENVIRONMENT=production
   PAYSTACK_MODE=live
   ```
3. **التشغيل عبر خادم Gunicorn مع عمال Uvicorn Workers:**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
4. **تفعيل شهادات الأمان HTTPS والوكيل العكسي (Reverse Proxy):** ضع السيرفر خلف Nginx أو Caddy مع تفعيل بروتوكول HSTS والتشفير الكامل.

---

## 13. دليل معالجة الأخطاء والأسئلة الشائعة (FAQ)

### س1: لماذا يرجع المسار `/quotes/today` رمز الخطأ `404 Not Found`؟
**السبب:** تم تشغيل السيرفر وقاعدة البيانات فارغة دون بذر الاقتباسات الـ 365.
**الحل:** قم بتشغيل سكربت البذر: `python scripts/seed_quotes.py`.

### س2: لماذا يرجع المسار `PATCH /users/me/password` خطأ `405 Method Not Allowed`؟
**السبب:** محاولة استدعاء المسار بطريقة `PUT` أو `POST`.
**الحل:** يتطلب مسار تغيير كلمة المرور استخدام طريقة `PATCH` حصراً.

### س3: لماذا يرجع فحص الدفع رمز `403 Forbidden`؟
**السبب:** درع حماية الملكية. لا يُسمح للمستخدم (أ) بالتحقق من معاملة دفع تخص المستخدم (ب).
**الحل:** تأكد من أن توكن المصادقة المرسل ينتمي لنفس المستخدم الذي أنشأ العملية.

---

## 14. الحوكمة المعمارية والترخيص

تم تطوير وصيانة هذا النظام البرمجي وفقاً لدستور هندسة بايثون المؤسسية (**Enterprise Python Architecture Constitution**):
- استخدام إشارات الأنابيب الحديثة (`|`) حصرًا لتعريف الأنواع في Python 3.10+. يُمنع استخدام `Union` أو `Optional`.
- استخدام نماذج Pydantic V2 لحماية حدود كافة العمليات الواردة والصادرة.
- التزام كافة الحزم بنمط الواجهة `__all__` لمنع التلوث النطاقي.
- انعدام الثقة في مدخلات العميل المالية والاعتماد الحصري على السيرفر.

---
*تم البناء والإتقان البرمجي لخدمة منظومة تطبيق تحفيز غانا (Aquaba).*
