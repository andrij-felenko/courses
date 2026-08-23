# 📋 Специфікація інструменту та матриця даних сервіс-аудиту Digital Homes

Цей довідник описує формальну специфікацію матриці аудіювання сервісних меж (Service Audit Matrix Specification), структури DTO аналізу зв'язаності (Coupling Analysis DTOs), правила розрахунку кількісного підсумкового бала виділення (Extraction Score Formula), Prometheus-метрики спостережуваності та CLI/API інтерфейси автоматизованого сканера меж кодової бази Digital Homes. Документ призначено для архітекторів, бекенд-розробників та DevSecOps інженерів, які проводять систематичний аудит монолітних систем перш ніж ухвалювати рішення про виділення мережевих меж.

---

## 1. Схема конфігурації аудиту та вагових коефіцієнтів (`audit-config.json`)

Сканер сервіс-аудиту приймає конфігураційний файл у форматі JSON, де задано порогові значення для кожного виміру зв'язаності, параметри підключення до бази даних та відносні вагові коефіцієнти для підрахунку підсумкового бала.

```json
{
  "$schema": "https://digitalhomes.io/schemas/service-audit-v1.json",
  "system_name": "digital-homes-monolith",
  "audit_version": "1.4.0",
  "analysis_period_days": 30,
  "data_sources": {
    "postgresql_log_path": "/var/log/postgresql/postgresql-query.log",
    "opentelemetry_endpoint": "http://otel-collector.internal:4317",
    "git_repository_path": "/src/digital-homes-monolith"
  },
  "weights": {
    "resource_asymmetry": 2.5,
    "deploy_autonomy": 2.0,
    "fault_isolation": 3.0,
    "compliance_isolation": 3.5,
    "data_coupling_penalty": -3.0,
    "sync_rpc_depth_penalty": -2.5,
    "distributed_tx_penalty": -4.0
  },
  "thresholds": {
    "min_extraction_score": 15.0,
    "max_allowed_data_coupling_score": 3.0,
    "max_sync_rpc_depth": 2,
    "max_cross_context_joins_per_sec": 5
  },
  "contexts": [
    {
      "id": "dh-device-mgmt",
      "name": "Device Management",
      "owner_team": "team-core-hardware",
      "tables": ["devices", "device_capabilities", "firmware_versions"],
      "deploy_frequency_per_month": 4,
      "compliance_level": "none"
    },
    {
      "id": "dh-digital-twin",
      "name": "Digital Twin Engine",
      "owner_team": "team-core-state",
      "tables": ["device_states", "device_desired_states", "shadow_reconciliations"],
      "deploy_frequency_per_month": 8,
      "compliance_level": "none"
    },
    {
      "id": "dh-automations",
      "name": "Automations Engine",
      "owner_team": "team-automation-rules",
      "tables": ["automation_rules", "rule_triggers", "rule_execution_logs"],
      "deploy_frequency_per_month": 12,
      "compliance_level": "none"
    },
    {
      "id": "dh-telemetry",
      "name": "Telemetry Ingestion",
      "owner_team": "team-data-platform",
      "tables": ["telemetry_events_raw", "sensor_time_series"],
      "deploy_frequency_per_month": 20,
      "compliance_level": "none"
    },
    {
      "id": "dh-video",
      "name": "Video Streaming",
      "owner_team": "team-media-video",
      "tables": ["video_feeds", "camera_configs"],
      "deploy_frequency_per_month": 15,
      "compliance_level": "none"
    },
    {
      "id": "dh-notifications",
      "name": "Notifications & Alerts",
      "owner_team": "team-user-engagement",
      "tables": ["push_tokens", "notification_history"],
      "deploy_frequency_per_month": 30,
      "compliance_level": "gdpr"
    },
    {
      "id": "dh-identity",
      "name": "Identity & Access",
      "owner_team": "team-security-auth",
      "tables": ["users", "user_credentials", "oauth_tokens", "access_policies"],
      "deploy_frequency_per_month": 2,
      "compliance_level": "soc2"
    },
    {
      "id": "dh-billing",
      "name": "Billing & Subscriptions",
      "owner_team": "team-finance",
      "tables": ["subscriptions", "payment_cards", "invoices", "ledger_entries"],
      "deploy_frequency_per_month": 2,
      "compliance_level": "pci-dss-level-1"
    }
  ]
}
```

### Пояснення полів конфігурації:
- **`system_name`:** Унікальний ідентифікатор цільової монолітної системи в реєстрі архітектурних активів.
- **`analysis_period_days`:** Часове вікно вибірки журналів запитів (за замовчуванням 30 днів), яке гарантує покриття пікових вечірніх та щомісячних білінг-навантажень.
- **`weights`:** Вагові коефіцієнти математичної моделі, що дозволяють налаштовувати чутливість сканера під специфіку домену (наприклад, збільшення вагомості комплаєнсу для фінансових систем).
- **`thresholds`:** Граничні межі відхилення. Якщо показник `max_sync_rpc_depth` перевищує 2, сканер генерує критичне застереження про ризик накопичення затримок.

---

## 2. Математична формула та правила підрахунку бала виділення (Extraction Score)

Підсумковий бал виділення кандидат-модуля `S_ext` обчислюється як зважена сума позитивних драйверів ізоляції за вирахуванням штрафів за зчеплення за даними, синхронними викликами та складністю розподілених транзакцій:

```
S_ext = (w1 · ResourceAsymmetry) + (2.0 · DeployAutonomy) + (3.0 · FaultIsolation) + (3.5 · Compliance)
        - (3.0 · DataCouplingScore) - (2.5 · SyncRPCDepth) - (4.0 · DistributedTxCost)
```

Де кожен параметр нормується за вільно вимірюваною шкалою від 0 до 10 на основі зібраних телеметричних даних:

### Драйвери винесення (Positive Drivers):
- **`ResourceAsymmetry` (0..10):** Виміряне відношення розриву ресурсного профілю (CPU, RAM, GPU, IOPS) порівняно із середнім значенням моноліта. Значення 10 відповідає розриву понад `15x` (наприклад, 15 000 IOPS телеметрії при середньому показникові моноліта 500 IOPS).
- **`DeployAutonomy` (0..10):** Частота релізів модуля на місяць. 10 відповідає понад `30` деплоям/місяць при середньому показникові моноліта `2` деплої/місяць, що вказує на тертя в релізному конвеєрі.
- **`FaultIsolation` (0..10):** Оцінка ризику системних крашів (OOM, SIGSEGV у C-бібліотеках, витоки пам'яті). 10 відповідає модулям з нестабільними зовнішніми native-залежностями (наприклад, FFmpeg у відеомодулі).
- **`Compliance` (0..10):** Рівень регуляторного тиску. 0 — немає вимог; 5 — GDPR/SOC2; 10 — PCI-DSS Level 1 або HIPAA (вимагають ізоляції в окремий зоновий файрвол).

### Штрафи за зчеплення (Coupling Penalties):
- **`DataCouplingScore` (0..10):** Кількість міждоменних SQL `JOIN`, прямих зовнішніх Foreign Keys та спільних таблиць БД. 0 — абсолютна відсутність зв'язків; 10 — модуль робить `JOIN` з 5+ таблицями інших контекстів.
- **`SyncRPCDepth` (0..10):** Максимальна глибина ланцюжка синхронних викликів, яку генерує або споживає модуль під час обробки бізнес-транзакції.
- **`DistributedTxCost` (0..10):** Оцінка кількості бізнес-операцій, які вимагатимуть впровадження паттерну Two-Phase Commit (2PC) або Saga у разі відокремлення модуля в мережу.

### Порогові класифікаційні рішення:
- **`S_ext ≥ 15.0` та `DataCouplingScore ≤ 3.0`:** 🟢 **Першочерговий кандидат на виділення** (Prime Extraction Candidate). Сервіс можна виносити в мережу негайно.
- **`S_ext ≥ 15.0` та `DataCouplingScore > 3.0`:** 🟡 **Кандидат на рефакторинг даних** (Data Refactoring Required First). Виносити в мережу заборонено до усунення SQL `JOIN` та розриву Foreign Keys.
- **`S_ext < 15.0` та `DataCouplingScore ≤ 3.0`:** ⚪ **Низький пріоритет винесення** (Low Priority). Заставити у моноліті, оскільки операційний чек перевищить виграш.
- **`S_ext < 15.0` та `DataCouplingScore > 3.0`:** 🔴 **Ядро моноліта** (Monolith Core). Виділяти заборонено.

---

## 3. Таблиця виміряної матриці сервіс-аудиту Digital Homes

Нижче наведено зведені результати аудиту 8 ключових контекстів платформи Digital Homes за підсумками аналізу логів продуктивної системи за 30 днів (трафік: 100 000 домогосподарств, 15,000 req/sec телеметрії).

| Контекст (Домен) | Resource Asymmetry | Deploy Autonomy | Fault Isolation | Compliance Wall | Data Coupling Score | Sync RPC Depth | Distributed Tx Cost | Підсумковий Extraction Score (`S_ext`) | Архітектурний вердикт аудиту |
|---|---|---|---|---|---|---|---|---|---|
| **Telemetry Ingestion** | 9.5 (15k IOPS) | 8.0 (20/mo) | 4.0 | 0.0 | **0.5** (Append-only) | 0.0 | 0.0 | **+38.5** | 🟢 **Першочерговий виніс у сервіс** |
| **Video Streaming** | 9.0 (GPU/FFmpeg) | 6.0 (15/mo) | **9.5** (OOM risks) | 0.0 | **1.0** (Self-contained) | 1.0 | 0.0 | **+44.5** | 🟢 **Першочерговий виніс у сервіс** |
| **Notifications** | 6.0 (Push spikes) | 9.0 (30/mo) | 3.0 | 3.0 (GDPR) | **2.0** (Async queue) | 1.0 | 0.5 | **+28.0** | 🟢 **Першочерговий виніс у сервіс** |
| **Billing & Cards** | 2.0 (Low TPS) | 2.0 (2/mo) | 2.0 | **10.0** (PCI-DSS) | **1.5** (Isolated Vault) | 1.0 | 2.0 | **+25.0** | 🟢 **Першочерговий виніс у сервіс** |
| **Identity & Access** | 5.0 (100% Reads) | 2.0 (2/mo) | 3.0 | 5.0 (SOC2) | **7.5** (User FKs everywhere)| 3.0 | 4.0 | **-6.5** (до рефакторингу) | 🟡 **Спочатку прибрати FK та додати JWKS** |
| **Automations Engine** | 7.0 (CPU rules) | 5.0 (12/mo) | 3.0 | 0.0 | **6.0** (Reads Twin state) | 2.0 | 3.0 | **+2.0** | 🔴 **Заставити у моноліті** |
| **Device Management** | 3.0 (Medium TPS) | 3.0 (4/mo) | 2.0 | 0.0 | **8.5** (JOIN with Twin) | 2.0 | 6.0 | **-18.0** | 🔴 **Ядро моноліта (Core)** |
| **Digital Twin** | 4.0 (State mirror) | 4.0 (8/mo) | 2.0 | 0.0 | **9.0** (Shared tables) | 2.0 | 7.0 | **-22.5** | 🔴 **Ядро моноліта (Core)** |

---

## 4. Специфікація HTTP/REST та gRPC API сервісу аудиту

Сервіс аудиту надає розробникам та CI/CD системи програмний інтерфейс для отримання поточного стану зчеплення меж та метрик топології.

### REST Endpoint: `GET /api/v1/audit/coupling-matrix`

Повертає поточну матрицю зчеплення за даними між усіма зареєстрованими контекстами.

#### Запит:
```http
GET /api/v1/audit/coupling-matrix?period=30d HTTP/1.1
Host: audit-service.internal
Accept: application/json
```

#### Відповідь (200 OK):
```json
{
  "timestamp": "2026-08-18T09:30:00Z",
  "period_days": 30,
  "edges": [
    {
      "source_context": "dh-digital-twin",
      "target_context": "dh-device-mgmt",
      "cross_context_joins_count": 425000,
      "cross_context_fk_count": 4,
      "coupling_severity": "CRITICAL",
      "recommendation": "BLOCK_EXTRACTION"
    },
    {
      "source_context": "dh-telemetry",
      "target_context": "dh-device-mgmt",
      "cross_context_joins_count": 0,
      "cross_context_fk_count": 0,
      "coupling_severity": "NONE",
      "recommendation": "ALLOW_EXTRACTION"
    }
  ]
}
```

### Пояснення відповіді API:
- **`cross_context_joins_count`:** Акумульована кількість операцій об'єднання таблиць між двома доменами за обраний період. Значення понад 100 000 сигналізує про критичну залежність.
- **`coupling_severity`:** Рівень загрози винесенню (`NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **`recommendation`:** Чітка рекомендація для конвеєра збірки (`ALLOW_EXTRACTION`, `REQUIRE_DATA_REFACTORING`, `BLOCK_EXTRACTION`).

---

## 5. Формат JSON-звіту виходу аудитора (`service-audit-report.json`)

Автоматизований аналізатор генерує вихідний звіт, який використовується в CI/CD конвеєрах як архітектурна фітнес-функція (Architecture Fitness Function) для запобігання появі нових несанкціонованих SQL `JOIN` між модулями.

```json
{
  "timestamp": "2026-08-18T09:30:00Z",
  "audit_duration_seconds": 142.5,
  "analyzed_sql_queries_count": 4850000,
  "analyzed_rpc_calls_count": 12300000,
  "summary": {
    "total_contexts": 8,
    "prime_extraction_candidates": 4,
    "data_refactoring_required": 1,
    "monolith_core_contexts": 3
  },
  "violations": [
    {
      "severity": "CRITICAL",
      "rule_id": "NO_CROSS_CONTEXT_FK",
      "source_context": "dh-automations",
      "target_context": "dh-device-mgmt",
      "details": "Foreign Key constraint 'fk_rules_device_id' connects automation_rules.device_id to devices.id directly in PostgreSQL schema public."
    },
    {
      "severity": "HIGH",
      "rule_id": "NO_CROSS_CONTEXT_JOIN",
      "source_context": "dh-digital-twin",
      "target_context": "dh-device-mgmt",
      "details": "Detected 1,420 queries/min executing 'SELECT * FROM device_states s JOIN devices d ON s.device_id = d.id'."
    }
  ],
  "recommendations": [
    {
      "step": 1,
      "action": "EXTRACT_SERVICE",
      "target_context": "dh-telemetry",
      "estimated_tco_saving_percent": 35.0,
      "prerequisites": ["Deploy NATS JetStream Outbox", "Migrate time-series table to TimescaleDB"]
    },
    {
      "step": 2,
      "action": "EXTRACT_SERVICE",
      "target_context": "dh-video",
      "estimated_tco_saving_percent": 15.0,
      "prerequisites": ["Isolate RTSP C-libraries into dedicated Docker container with GPU pass-through"]
    },
    {
      "step": 3,
      "action": "REFACTOR_DATA_FIRST",
      "target_context": "dh-identity",
      "prerequisites": ["Replace synchronous Auth RPC with local JWKS public key verification in API Gateway", "Remove FK constraints on user_id in billing_cards table"]
    }
  ]
}
```

---

## 6. Метрики спостережуваності Prometheus (`metrics`)

Сканер аудиту експортує Prometheus-метрики для побудови моніторингових панелей у Grafana:

```prometheus
# HELP dh_audit_cross_context_joins_total Загальна кількість виявлених міждоменних SQL JOIN
# TYPE dh_audit_cross_context_joins_total counter
dh_audit_cross_context_joins_total{source="dh-digital-twin",target="dh-device-mgmt"} 425000
dh_audit_cross_context_joins_total{source="dh-telemetry",target="dh-device-mgmt"} 0

# HELP dh_audit_extraction_score Поточний бал доцільності виділення модуля
# TYPE dh_audit_extraction_score gauge
dh_audit_extraction_score{context="dh-telemetry"} 38.5
dh_audit_extraction_score{context="dh-video"} 44.5
dh_audit_extraction_score{context="dh-device-mgmt"} -18.0
dh_audit_extraction_score{context="dh-digital-twin"} -22.5

# HELP dh_audit_sync_rpc_depth Глибина ланцюжка синхронних викликів
# TYPE dh_audit_sync_rpc_depth gauge
dh_audit_sync_rpc_depth{context="dh-identity"} 3.0
dh_audit_sync_rpc_depth{context="dh-telemetry"} 0.0
```

За допомогою даних метрик DevSecOps команди налаштовують сповіщення (Alerting Rules): якщо у будь-якому модулі з високим балом виділення (наприклад, `dh-telemetry`) з'являється `dh_audit_cross_context_joins_total > 0`, чергова зміна блокується на етапі рев'ю.

---

## 7. Специфікація CLI-команд аналізатора (`dh-audit-cli`)

Інструмент аудиту поставляється у вигляді бінарного файлу або Docker-контейнера `dh-audit-cli`.

### Основні опції виклику:

```bash
# Провести повний аудит кодової бази та логів запитів PostgreSQL
dh-audit-cli scan \
  --config=./audit-config.json \
  --repo-path=/src/digital-homes-monolith \
  --pg-log-path=/var/log/postgresql/postgresql-query.log \
  --output=json \
  --report-file=./service-audit-report.json

# Перевірити дотримання архітектурних меж у CI/CD (повертає exit code 1 при порушеннях)
dh-audit-cli check-boundaries \
  --config=./audit-config.json \
  --max-allowed-cross-joins=0 \
  --fail-on-critical
```

### Специфікація кодів повернення (Exit Codes):
- **`0`:** Аудит пройшов успішно, порушень меж та нових зчеплень не виявлено.
- **`1`:** Виявлено критичні порушення меж (наприклад, поява нового SQL `JOIN` між майбутнім мікросервісом та ядром моноліта).
- **`2`:** Невалідний конфігураційний файл або відсутній доступ до логів БД.
- **`3`:** Перевищено порогове значення глибини синхронних RPC-викликів (`SyncRPCDepth > 2`).
