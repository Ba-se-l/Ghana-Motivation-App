# 🐘 الدليل الهندسي الشامل لترحيل وإدارة المشروع عبر Alembic و PostgreSQL

> **الدليل المرجعي الصارم للمهندسين والمطورين لنقل البنية التحتية لمشروع Ghana Motivation Backend من SQLite و `create_all()` إلى بنية الترحيلات المهنية القابلة للتوسع عبر Alembic ومحرك قواعد البيانات عالي الأداء PostgreSQL.**

---

## 📑 فهرس المحتويات
1. [المقدمة الهندسية ومسوغات الترحيل (Architectural Justification)](#1-المقدمة-الهندسية-ومسوغات-الترحيل-architectural-justification)
2. [خارطة المهام الهرمية للتحول الكامل (Hierarchical WBS Action Roadmap)](#2-خارطة-المهام-الهرمية-للتحول-الكامل-hierarchical-wbs-action-roadmap)
3. [الملفات البرمجية الواجب تعديلها في المشروع (Surgical Modifications)](#3-الملفات-البرمجية-الواجب-تعديلها-في-المشروع-surgical-modifications)
   - [الملف الأول: `GhanaMotivationApp/database/engine.py`](#الملف-الأول-ghanamotivationappdatabaseenginepy)
   - [الملف الثاني: `main.py`](#الملف-الثاني-mainpy)
   - [الملف الثالث: ملف البيئة `.env`](#الملف-الثالث-ملف-البيئة-env)
4. [هندسة وإعداد ملفات ترحيل Alembic](#4-هندسة-وإعداد-ملفات-ترحيل-alembic)
   - [ملف الضبط العام: `alembic.ini`](#ملف-الضبط-العام-alembicini)
   - [ملف البيئة غير المتزامنة: `alembic/env.py`](#ملف-البيئة-غير-المتزامنة-alembicenvpy)
   - [قالب الترحيل: `alembic/script.py.mako`](#قالب-الترحيل-alembicscriptpymako)
5. [دليل الأوامر التشغيلي لـ Alembic (Operational Runbook & Cheatsheet)](#5-دليل-الأوامر-التشغيلي-لـ-alembic-operational-runbook--cheatsheet)
6. [الفخاخ التقنية في PostgreSQL والحلول الوقائية (Pitfalls & Gotchas)](#6-الفخاخ-التقنية-في-postgresql-والحلول-الوقائية-pitfalls--gotchas)
7. [خيارات تشغيل وتجهيز PostgreSQL: محلياً بدون Docker، سحابياً، أو عبر Docker](#7-خيارات-تشغيل-وتجهيز-postgresql-محليا-بدون-docker-سحابيا-أو-عبر-docker)
   - [الخيار الأول: التثبيت المحلي المباشر على نظام التشغيل (بدون Docker)](#الخيار-الأول-التثبيت-المحلي-المباشر-على-نظام-التشغيل-بدون-docker)
   - [الخيار الثاني: استخدام قاعدة بيانات سحابية مجانية فورية (بدون Docker وبدون تثبيت)](#الخيار-الثاني-استخدام-قاعدة-بيانات-سحابية-مجانية-فورية-بدون-docker-وبدون-تثبيت)
   - [الخيار الثالث: التشغيل السريع عبر بيئة Docker Compose المرفقة](#الخيار-الثالث-التشغيل-السريع-عبر-بيئة-docker-compose-المرفقة)

---

## 1. المقدمة الهندسية ومسوغات الترحيل (Architectural Justification)

في بيئة التطوير الأولية (Beta/MVP)، كان التطبيق يعتمد على قاعدة بيانات **SQLite** عبر مكتبة `aiosqlite` ويقوم بإنشاء الجداول عند الإقلاع باستخدام دالة `Base.metadata.create_all()` داخل دورة حياة السيرفر `lifespan`. 

بالرغم من بساطة هذا الأسلوب في بداية التطوير، إلا أنه **غير صالح تماماً للإنتاج (Production Disaster)** للأسباب الهندسية التالية:

### لماذا يجب التخلي عن `Base.metadata.create_all()`؟
1. **استحالة تعديل الجداول بدون تدمير البيانات:** دالة `create_all()` تقوم بإنشاء الجداول *إذا لم تكن موجودة فقط*. في حال قمت بإضافة عمود جديد أو تغيير نوع حقل لاحقاً، لن تفعل الدالة أي شيء، وسيرمي التطبيق خطأً يطلب إعادة حذف قاعدة البيانات بالكامل لبنائها من جديد!
2. **غياب التتبع التاريخي وتضارب التفرعات:** لا يوجد أي سجل يوضح من قام بتعديل بنية البيانات، متى تم ذلك، وما هي التعديلات المتسلسلة (Schema Versioning).
3. **مخاطر تضارب التزامن عند النشر:** في بيئات الإنتاج التي تشغل خوادم متعددة (Multiple Workers/Replicas)، يؤدي استدعاء `create_all` عند إقلاع كل حاوية إلى حدوث حالات سباق (Race Conditions) وتضارب على مستوى قفل المخطط.

### لماذا PostgreSQL ومكتبة `asyncpg`؟
1. **تعدد الاتصالات المتزامنة الحقيقية (True Concurrency):** تقوم SQLite بقفل الملف بالكامل أثناء عمليات الكتابة (`database is locked`)، بينما تعتمد PostgreSQL على معمارية MVCC (Multi-Version Concurrency Control) التي تتيح آلاف عمليات القراءة والكتابة المتزامنة بدون أي تعليق.
2. **مجمع الاتصالات الفعلي (True Connection Pooling):** يدعم محرك PostgreSQL مجمعات اتصالات عالية الكفاءة (`pool_size` و `max_overflow`) لإعادة تدوير الاتصالات وتقليل تكلفة فتح المقابس (Sockets).
3. **الدقة التامة في أنواع البيانات الزمنية والعملات:** دعم أصيل للتواريخ ذات المناطق الزمنية `TIMESTAMP WITH TIME ZONE` (والتي تفتقر إليها SQLite وتخزنها كنصوص غير محددة المنطقة)، بالإضافة للتحكم الدقيق في القيود والفهارس.

---

## 2. خارطة المهام الهرمية للتحول الكامل (Hierarchical WBS Action Roadmap)

لتنفيذ الترحيل بنجاح 100% دون أي مفاجآت، اتبع هذه الخارطة المتسلسلة خطوة بخطوة:

```mermaid
graph TD
    P1[المرحلة 1: تشغيل خادم PostgreSQL] --> P2[المرحلة 2: التعديلات الجراحية في الكود]
    P2 --> P3[المرحلة 3: استخراج ملفات تهيئة Alembic]
    P3 --> P4[المرحلة 4: ربط Alembic بالنماذج والإعدادات]
    P4 --> P5[المرحلة 5: توليد وتطبيق ترحيل الأساس Initial Revision]
    P5 --> P6[المرحلة 6: بذر البيانات والاقتباسات الـ 365]
    P6 --> P7[المرحلة 7: تشغيل الفحص والاعتماد النهائي tests/]
```

### [ ] المرحلة 1: تشغيل وتجهيز خادم PostgreSQL (اختر أحد المسارات الثلاثة)
- [ ] **المسار أ (بدون Docker محلياً):** تثبيت PostgreSQL مباشرة على Windows / Linux وتشغيل الخدمة وإنشاء المستخدم `ghana_admin` وقاعدة البيانات `ghana_motivation_db` عبر `psql` (راجع [القسم 7 بالتفصيل](#الخيار-الأول-التثبيت-المحلي-المباشر-على-نظام-التشغيل-بدون-docker)).
- [ ] **المسار ب (بدون Docker وبدون تثبيت - سحابياً):** إنشاء مشروع مجاني على Neon.tech أو Supabase ونسخ رابط الاتصال ولصقه مباشرة في `.env` (راجع [القسم 7](#الخيار-الثاني-استخدام-قاعدة-بيانات-سحابية-مجانية-فورية-بدون-docker-وبدون-تثبيت)).
- [ ] **المسار ج (عبر Docker):** تشغيل الحاوية المجهزة المرفقة:
  ```powershell
  docker compose -f alembic_docs/docker-compose.postgres.yml up -d
  ```
- [ ] التحقق من أن الخادم يستقبل الاتصالات بنجاح وجاهزية قاعدة البيانات.

### [ ] المرحلة 2: تنفيذ التعديلات الجراحية في كود المشروع
- [ ] تعديل `GhanaMotivationApp/database/engine.py` لدعم مجمع الاتصالات لـ PostgreSQL واستثناء SQLite.
- [ ] تعديل `main.py` بإيقاف استدعاء `await create_all_tables()` من دورة حياة السيرفر.
- [ ] تعديل ملف البيئة `.env` لتوجيه `DATABASE_URL` نحو رابط `postgresql+asyncpg`.

### [ ] المرحلة 3: تجهيز بنية مجلد ترحيلات Alembic
- [ ] إنشاء مجلد `alembic/` ومجلد الترحيلات الفرعي `alembic/versions/` في جذر المشروع.
- [ ] نسخ ملفات القوالب الجاهزة من `alembic_docs/templates/` إلى أماكنها المعتمدة:
  - نسخ `alembic_docs/templates/alembic.ini` إلى جذر المشروع: `./alembic.ini`.
  - نسخ `alembic_docs/templates/env.py` إلى: `./alembic/env.py`.
  - نسخ `alembic_docs/templates/script.py.mako` إلى: `./alembic/script.py.mako`.

### [ ] المرحلة 4: التحقق من ربط Alembic غير المتزامن
- [ ] فحص كود `alembic/env.py` والتأكد من احتوائه على استيراد كافة نماذج المشروع الخمسة (`User`, `RefreshSession`, `Payment`, `Subscription`, `Quote`) لربطها بـ `target_metadata = Base.metadata`.

### [ ] المرحلة 5: توليد الترحيل الأساسي وتطبيقه على قاعدة البيانات
- [ ] توليد أول ملف ترحيل تلقائي بالكامل:
  ```powershell
  alembic revision --autogenerate -m "initial_schema"
  ```
- [ ] مراجعة ملف الترحيل المنشأ في `alembic/versions/` والتأكد من صحة الجداول الخمسة.
- [ ] تطبيق الترحيل على قاعدة البيانات:
  ```powershell
  alembic upgrade head
  ```

### [ ] المرحلة 6: بذر البيانات (Seeding)
- [ ] بذر بيانات الاقتباسات الـ 365 في قاعدة بيانات PostgreSQL الجديدة:
  ```powershell
  python scripts/seed_quotes.py
  ```

### [ ] المرحلة 7: الفحص والاعتماد النهائي (Verification & Sign-off)
- [ ] تشغيل خادم Uvicorn أو تشغيل حزمة الاختبارات الشاملة للتأكد من نجاح كل الفحوصات:
  ```powershell
  python tests/run_all_tests.py
  ```

---

## 3. الملفات البرمجية الواجب تعديلها في المشروع (Surgical Modifications)

يجب إجراء تعديلات جراحية دقيقة على ثلاثة ملفات في المشروع لضمان التوافق الكامل. إليك التعديلات بالتفصيل:

---

### الملف الأول: `GhanaMotivationApp/database/engine.py`

#### الهدف الهندسي:
محرك SQLite لا يقبل باراميترات تجميع الاتصال مثل `pool_size` أو `max_overflow` إذا لم يُستخدم مجمع مناسب، بينما تتطلب PostgreSQL هذه المعاملات للاستفادة من إدارة الاتصالات المتزامنة. يجب جعل إنشاء المحرك ديناميكياً وذكياً بناءً على نوع رابط قاعدة البيانات.

#### 🔴 قبل التعديل [BEFORE]:
```python
# Global asynchronous SQLAlchemy engine instance bound to database URL
async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.ECHO,
)
```

#### 🟢 بعد التعديل [AFTER]:
```python
from sqlalchemy.pool import NullPool

# Determine if the target database is SQLite or PostgreSQL
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Build engine arguments dynamically
engine_kwargs = {
    "echo": settings.ECHO,
}

if is_sqlite:
    # SQLite development fallback: NullPool ensures no locked connection retention
    engine_kwargs["poolclass"] = NullPool
else:
    # PostgreSQL production pooling settings
    engine_kwargs["pool_size"] = settings.POOL_SIZE
    engine_kwargs["max_overflow"] = settings.MAX_OVERFLOW
    engine_kwargs["pool_timeout"] = settings.POOL_TIMEOUT

# Global asynchronous SQLAlchemy engine instance
async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    **engine_kwargs,
)
```

---

### الملف الثاني: `main.py`

#### الهدف الهندسي:
إلغاء إنشاء الجداول التلقائي المباشر `create_all_tables()` من الـ `lifespan`، وتسليم مسؤولية إدارة المخطط بالكامل وبشكل احترافي لأداة Alembic قبل إقلاع التطبيق (في خطوة CI/CD أو عبر سكربت تشغيل الحاوية).

#### 🔴 قبل التعديل [BEFORE]:
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifecycle events.

    On startup: Connects to the database and creates all tables if
    they don't already exist.
    On shutdown: Closes the database engine.
    """
    
    # للتجربة هون بس منستخدم هي الدالة (create_database) | لازم نستخدم (Alembic)
    await create_all_tables()
    
    yield
```

#### 🟢 بعد التعديل [AFTER]:
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifecycle events.

    In production with PostgreSQL + Alembic, schema management is strictly
    delegated to migration scripts (e.g. `alembic upgrade head`) before process startup.
    Automatic `create_all_tables` is disabled to prevent race conditions across workers.
    """
    logger.info("Starting Ghana Motivation API engine...")
    
    yield
    
    logger.info("Shutting down database engine...")
    await async_engine.dispose()
```

---

### الملف الثالث: ملف البيئة `.env`

#### الهدف الهندسي:
توجيه التطبيق للاتصال بخادم PostgreSQL عبر مشغل `asyncpg` غير المتزامن، وضبط بيئة العمل.

#### 🔴 قبل التعديل [BEFORE]:
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
ENVIRONMENT=development
```

#### 🟢 بعد التعديل [AFTER]:
```env
# PostgreSQL connection string via asyncpg driver
DATABASE_URL=postgresql+asyncpg://ghana_admin:ghana_secure_password_2026!@localhost:5432/ghana_motivation_db

# Connection Pool Settings
POOL_SIZE=10
MAX_OVERFLOW=20
POOL_TIMEOUT=30

# Environment Mode
ENVIRONMENT=development
```

---

## 4. هندسة وإعداد ملفات ترحيل Alembic

تم إعداد وتوفير قوالب جاهزة بالكامل داخل المجلد `alembic_docs/templates/`. فيما يلي شرح تفصيلي لدور كل ملف وكيفية إعداده:

### ملف الضبط العام: `alembic.ini`
يُوضع في جذر المشروع (`ghana-motivation-backend/alembic.ini`). أهم محتوياته:
- `script_location = alembic`: يحدد مجلد كود الترحيلات.
- `version_locations = alembic/versions`: يحدد مجلد ملفات الـ Revisions.
- `file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s`: يضمن تسمية الترحيلات بتاريخ ووقت التوليد لترتيب الملفات زمنياً بشكل أنيق.
- `sqlalchemy.url`: يتم تعريفه كقيمة افتراضية ولكن يتم تجاوزه ديناميكياً من ملف الإعدادات داخل `env.py`.

---

### ملف البيئة غير المتزامنة: `alembic/env.py`
هذا الملف هو العقل المدبر لـ Alembic. لضمان توافقه مع معمارية تطبيقنا ومكتبة SQLAlchemy 2.0 Async:
1. **استيراد النماذج (Model Registry Pattern):**
   يقوم الملف باستيراد كافة النماذج الخمسة صراحة:
   ```python
   from GhanaMotivationApp.database.base import Base
   from GhanaMotivationApp.modules.auth.model import RefreshSession
   from GhanaMotivationApp.modules.user.model import User
   from GhanaMotivationApp.modules.payment.model import Payment
   from GhanaMotivationApp.modules.subscription.model import Subscription
   from GhanaMotivationApp.modules.quote.model import Quote

   target_metadata = Base.metadata
   ```
   *الفائدة:* بدون هذه الاستيرادات، لن يعرف Alembic بوجود الجداول وسيقوم بتوليد ملف ترحيل فارغ!

2. **الربط الديناميكي مع إعدادات التطبيق:**
   ```python
   from GhanaMotivationApp.settings import settings
   config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
   ```
   *الفائدة:* يضمن أن الترحيلات تعمل دائماً على نفس الرابط المحدد في ملف `.env` دون الحاجة لتكرار كتابته يدوياً في `alembic.ini`.

3. **التنفيذ غير المتزامن (Async Engine):**
   يستخدم الدالة:
   ```python
   async def run_async_migrations():
       connectable = async_engine_from_config(...)
       async with connectable.connect() as connection:
           await connection.run_sync(do_run_migrations)
   ```
   لتنفيذ أوامر SQL عبر المحرك غير المتزامن الخاص بـ SQLAlchemy.

---

### قالب الترحيل: `alembic/script.py.mako`
يُحدد الهيكل البرمجي الذي يتم توليد ملفات الترحيل بناءً عليه داخل `alembic/versions/`. يحتوي على دالتي `upgrade()` و `downgrade()`.

---

## 5. دليل الأوامر التشغيلي لـ Alembic (Operational Runbook & Cheatsheet)

احتفظ بهذا الجدول كمرجع سريع للعمليات اليومية وإدارة الترحيلات:

| الأمر (Command) | الوظيفة الهندسية | متى يُستخدم؟ |
|---|---|---|
| `alembic revision --autogenerate -m "وصف التعديل"` | مقارنة نماذج الكود بقاعدة البيانات وتوليد ملف ترحيل تلقائي جديد | عند إضافة جدول، عمود، تعديل نوع حقل، أو إضافة فهرس في مجلد `models/` |
| `alembic upgrade head` | تطبيق كافة الترحيلات المعلقة والانتقال لأحدث إصدار للمخطط | قبل تشغيل السيرفر، في خطوات الـ CI/CD، أو بعد سحب كود جديد (git pull) |
| `alembic downgrade -1` | التراجع عن آخر ترحيل تم تطبيقه خطوة واحدة للخلف | في حال وجود خطأ في آخر ترحيل وتريد تصحيحه |
| `alembic downgrade base` | إلغاء كافة الترحيلات والرجوع لقاعدة بيانات فارغة تماماً | في بيئة التطوير عند الرغبة في إعادة البناء من الصفر |
| `alembic current` | عرض معرف الترحيل (Revision ID) النشط حالياً في قاعدة البيانات | للتحقق من المخطط المعمول به في السيرفر الآن |
| `alembic history --verbose` | عرض شجرة وسجل الترحيلات بالكامل مع التواريخ والشروحات | لمعاينة التغيرات التاريخية للمشروع بالترتيب الزمني |
| `alembic check` | التحقق مما إذا كانت هناك تعديلات في نماذج الكود لم يتم توليد ترحيل لها | يُستخدم في فحص الـ CI لمنع دمج كود بدون ملفات ترحيله |
| `alembic merge heads -m "دمج تفرعين"` | دمج فرعين منفصلين من الترحيلات في فرع واحد | عند حدوث تضارب ناتج عن عمل مطورين على فرعين مختلفين (Branching) |

---

## 6. الفخاخ التقنية في PostgreSQL والحلول الوقائية (Pitfalls & Gotchas)

عند الانتقال من SQLite إلى PostgreSQL، هناك عدة فخاخ برمجية يقع فيها المطورون؛ تم تحصين مشروعنا ضدها بالكامل:

### الفخ 1: أنواع الـ Enum في PostgreSQL (Native vs String Enum)
* **المشكلة:** في SQLite يتم تخزين الـ Enum كنص عادي (VARCHAR). في PostgreSQL، يقوم SQLAlchemy بشكل افتراضي بإنشاء نوع بيانات مخصص على مستوى السيرفر عبر `CREATE TYPE ... AS ENUM`. إذا حاول Alembic تطبيق الترحيل والنوع موجود مسبقاً، قد يحدث خطأ `DuplicateObject`.
* **الحل الوقائي المعتمد:**
  في نماذج البيانات، تم ضبط الـ Enum ليعمل بنمط `native_enum=False` أو استخدام نصوص معتمدة، مما يخزن القيم كنصوص محمية بـ Python Enums ويمنع قفل المخطط.

---

### الفخ 2: حساسية التواريخ والمناطق الزمنية (Naive vs Aware UTC)
* **المشكلة:** كانت SQLite تقبل التواريخ مجردة من المنطقة الزمنية (Naive Datetimes). محرك `asyncpg` في PostgreSQL يفرض فحصاً صارماً: إذا كان الحقل معرفاً كـ `DateTime(timezone=True)`، فإن محاولة إدخال تاريخ Naive سترمي خطأ استثناء فوراً!
* **الحل الوقائي المعتمد:**
  كافة التواريخ في مشروعنا تستخدم الآن `datetime.now(timezone.utc)` بشكل صارم، ونماذج SQLAlchemy تستخدم `DateTime(timezone=True)` لإنشاء حقول `TIMESTAMP WITH TIME ZONE` متوافقة 100%.

---

### الفخ 3: مشكلة مجمع الاتصالات مع PgBouncer (Prepared Statements)
* **المشكلة:** مشغل `asyncpg` يقوم بتخزين الاستعلامات المجهزة مسبقاً (Prepared Statements) لتحقيق أعلى أداء. إذا تم وضع التطبيق خلف مجمع اتصالات خارجي مثل PgBouncer في وضع Transaction Pooling، سيرمي التطبيق أخطاء `duplicate prepared statement`.
* **الحل الوقائي المعتمد:**
  في حال استخدام PgBouncer لاحقاً، يتم تمرير المعامل التالي في رابط قاعدة البيانات:
  `postgresql+asyncpg://...?prepared_statement_cache_size=0`
  أما عند الاتصال المباشر بـ PostgreSQL (وهو النمط الافتراضي الموصى به لمشروعنا)، فإن إعدادات الـ Engine الافتراضية تعطي أقصى سرعة ممكنة.

---

## 7. خيارات تشغيل وتجهيز PostgreSQL: محلياً بدون Docker، سحابياً، أو عبر Docker

إذا كنت لا تستطيع تثبيت Docker أو لا ترغب في استخدامه على جهازك، فلديك **طريقتان سهلتان واحترافيتان تماماً** لتشغيل PostgreSQL لمشروعنا:

---

### الخيار الأول: التثبيت المحلي المباشر على نظام التشغيل (بدون Docker)

#### 1. خطوات التثبيت على نظام Windows:
1. قم بتحميل المثبت الرسمي لـ PostgreSQL (الإصدار 15 أو 16) لنظام Windows من موقع EnterpriseDB الرسمي:
   - [تحميل PostgreSQL الرسمي لنظام Windows](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
2. شغّل ملف التثبيت (`postgresql-16.x-windows-x64.exe`):
   - في خطوة اختيار المكونات، احتفظ بالاختيارات الافتراضية:
     - `PostgreSQL Server`
     - `pgAdmin 4` (واجهة رسومية لإدارة قواعد البيانات)
     - `Command Line Tools` (أدوات سطر الأوامر مثل `psql`)
   - في خطوة **Password**: أدخل كلمة مرور لحساب المدير الافتراضي `postgres` (مثلاً: `root` أو `postgres` واحفظها).
   - في خطوة **Port**: احتفظ بالمنفذ الافتراضي `5432`.
   - في خطوة **Locale**: اتركها افتراضية `[Default locale]`.
3. اضغط **Next** حتى يكتمل التثبيت. عند ظهور نافذة "Stack Builder" في النهاية، قم بإلغاء التحديد واضغط **Finish**.

#### 2. التحقق من أن خادم PostgreSQL يعمل على Windows:
افتح PowerShell وتحقق من أن الخدمة تعمل:
```powershell
Get-Service postgresql*
```
ستظهر لك الخدمة بحالة `Running`.

#### 3. إنشاء المستخدم وقاعدة البيانات الخاصة بمشروعنا عبر سطر الأوامر (`psql`):
افتح نافذة PowerShell أو Command Prompt واكتب الأمر التالي لتسجيل الدخول كمدير للنظام (سيطلب منك كلمة المرور التي اخترتها أثناء التثبيت):
```powershell
psql -U postgres
```
بمجرد دخولك إلى موجه أوامر PostgreSQL (`postgres=#`)، انسخ ونفّذ أوامر الـ SQL التالية بالترتيب:

```sql
-- 1. إنشاء المستخدم المعتمد لمشروعنا وكلمة مروره
CREATE USER ghana_admin WITH PASSWORD 'ghana_secure_password_2026!';

-- 2. إنشاء قاعدة البيانات وتعيين المستخدم كمالك لها
CREATE DATABASE ghana_motivation_db OWNER ghana_admin;

-- 3. منح كافة الصلاحيات على قاعدة البيانات للمستخدم
GRANT ALL PRIVILEGES ON DATABASE ghana_motivation_db TO ghana_admin;

-- 4. الاتصال بقاعدة البيانات الجديدة لضبط صلاحيات المخطط العام public (مهم جداً في PostgreSQL 15+)
\c ghana_motivation_db

-- 5. منح المستخدم صلاحيات إنشاء الجداول والجلسات داخل المخطط public
GRANT ALL ON SCHEMA public TO ghana_admin;
GRANT USAGE, CREATE ON SCHEMA public TO ghana_admin;

-- 6. الخروج من psql
\q
```

#### 4. البديل الرسومي عبر pgAdmin 4 (اختياري لمن يفضل الواجهات):
- افتح تطبيق **pgAdmin 4** من قائمة ابدأ.
- اتصل بالسيرفر المحلي `Servers -> PostgreSQL 16`.
- اضغط بالزر الأيمن على `Login/Group Roles -> Create -> Login/Group Role`:
  - الاسم: `ghana_admin`
  - في تبويب Definition كلمة المرور: `ghana_secure_password_2026!`
  - في تبويب Privileges فعّل: `Can login`.
- اضغط بالزر الأيمن على `Databases -> Create -> Database`:
  - الاسم: `ghana_motivation_db`
  - المالك (Owner): `ghana_admin`.

الآن أصبح خادم PostgreSQL جاهزاً تماماً محلياً، ورابط الاتصال في ملف `.env` الخاص بك سيعمل فوراً:
```env
DATABASE_URL=postgresql+asyncpg://ghana_admin:ghana_secure_password_2026!@localhost:5432/ghana_motivation_db
```

---

#### خطوات التثبيت السريع على أنظمة Linux (Ubuntu / Debian):
```bash
# تثبيت الحزم
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# التأكد من تشغيل الخدمة
sudo systemctl start postgresql
sudo systemctl enable postgresql

# الدخول وتنفيذ أوامر إنشاء المستخدم وقاعدة البيانات
sudo -u postgres psql -c "CREATE USER ghana_admin WITH PASSWORD 'ghana_secure_password_2026!';"
sudo -u postgres psql -c "CREATE DATABASE ghana_motivation_db OWNER ghana_admin;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ghana_motivation_db TO ghana_admin;"
sudo -u postgres psql -d ghana_motivation_db -c "GRANT ALL ON SCHEMA public TO ghana_admin;"
```

#### خطوات التثبيت السريع على أنظمة macOS (عبر Homebrew):
```bash
brew install postgresql@16
brew services start postgresql@16
psql postgres -c "CREATE USER ghana_admin WITH PASSWORD 'ghana_secure_password_2026!';"
psql postgres -c "CREATE DATABASE ghana_motivation_db OWNER ghana_admin;"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE ghana_motivation_db TO ghana_admin;"
psql -d ghana_motivation_db -c "GRANT ALL ON SCHEMA public TO ghana_admin;"
```

---

### الخيار الثاني: استخدام قاعدة بيانات سحابية مجانية فورية (بدون Docker وبدون تثبيت)

إذا كنت لا تريد تنزيل وتثبيت أي برامج على جهازك على الإطلاق، يمكنك الحصول على قاعدة بيانات PostgreSQL سحابية مجانية احترافية خلال 30 ثانية:

#### الخيار السحابي الأسهل: [Neon.tech](https://neon.tech)
1. توجه لموقع [Neon.tech](https://neon.tech) وسجل دخول مجاناً بحساب GitHub.
2. أنشئ مشروعاً جديداً باسم `ghana-motivation`.
3. سيعطيك الموقع فوراً رابط اتصال (Connection String) جاهز يبدأ بـ:
   `postgresql://username:password@ep-xyz.neon.tech/neondb?sslmode=require`
4. **الخطوة الوحيدة المطلوبة:** قم بتغيير البادئة من `postgresql://` إلى `postgresql+asyncpg://`، ثم الصق الرابط في ملف `.env` لمشروعك:
   ```env
   DATABASE_URL=postgresql+asyncpg://username:password@ep-xyz.neon.tech/neondb?sslmode=require
   ```
5. بهذه الخطوة البسيطة فقط، أصبح لديك خادم PostgreSQL سحابي حقيقي وسريع ومجاني بالكامل دون الحاجة لأي تثبيت محلي!

---

### الخيار الثالث: التشغيل السريع عبر بيئة Docker Compose المرفقة

لمن يمتلك Docker مثبت على جهازه ويرغب في بيئة معزولة ونظيفة بضغطة زر واحدة:

تم توفير ملف [`docker-compose.postgres.yml`](file:///d:/_Python%20Projects-27-05-2026/ghana-motivation-backend/alembic_docs/docker-compose.postgres.yml) الجاهز داخل مجلد `alembic_docs/`.

#### أمر التشغيل:
```powershell
docker compose -f alembic_docs/docker-compose.postgres.yml up -d
```

سيبدأ تشغيل حاوية PostgreSQL 16 الرسمية بالبيانات التالية:
- **المضيف:** `localhost`
- **المنفذ:** `5432`
- **اسم قاعدة البيانات:** `ghana_motivation_db`
- **المستخدم:** `ghana_admin`
- **كلمة المرور:** `ghana_secure_password_2026!`
- **التخزين الدائم:** عبر Volume محلي باسم `ghana_postgres_data`.

#### فحص جاهزية الحاوية:
```powershell
docker ps --filter "name=ghana_motivation_postgres"
```

---

### 🎯 الخلاصة التنفيذية
أياً كان المسار الذي تختاره من الخيارات الثلاثة أعلاه:
1. بمجرد أن تصبح قاعدة البيانات جاهزة وتستقبل الاتصال.
2. توجّه لتحديث رابط `DATABASE_URL` في ملف `.env`.
3. ابدأ بتوليد الترحيلات عبر:
   ```powershell
   alembic revision --autogenerate -m "initial_schema"
   alembic upgrade head
   ```
وسيعمل المشروع بنسبة 100% بكامل كفاءته واستقراره!

---
*تم إعداد هذا المرجع المعماري لضمان أعلى معايير الجودة والاستقرار لمشروع Ghana Motivation Backend.*
