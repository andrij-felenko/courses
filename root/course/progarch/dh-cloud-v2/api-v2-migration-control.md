# 📋 Специфікація API управління міграцією та фітнес-метрик v2

Ця вставка містить нормативну інженерну специфікацію API управління міграцією цифрових твінів платформи Digital Homes v2 (перехід з Варіанта Б у Варіант В), описує REST та gRPC контракти перемикання фаз, заголовки забезпечення когерентності кешу `Read-Your-Writes`, реєстр метрик спостережливості Prometheus для моніторингу архітектурного дрейфу та протокол обробки аварійних повідомлень у Dead Letter Queue (DLQ).

---

## 1. Архітектура панелі управління міграційним контуром

Під час 4-фазної zero-downtime міграції цифрового твінера Digital Homes із синхронного моноліту v1 (PostgreSQL) у гео-розподілений Event-Driven CQRS рушій v2 (Kafka + ScyllaDB) виникає потреба в централізованому та суворо захищеному інструменті керування прапорцями міграції.

Управління міграційними прапорцями (Feature Flags), регулювання швидкості фонового заповнення історичних даних (Token Bucket Backfill Rate Limit) та двосторонній перехід між фазами здійснюється через закритий адміністративний сервіс `Migration Control Plane`.

```
                        ┌──────────────────────────────┐
                        │   Migration Control Plane    │
                        │  (Admin REST & gRPC API)     │
                        └──────────────┬───────────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                ▼                      ▼                      ▼
       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
       │ Edge Fleet Router│    │ Twin Engine v2  │    │ Backfill Processor│
       │ (Feature Flags) │    │ (Read Switch)   │    │ (Token Bucket)  │
       └─────────────────┘    └─────────────────┘    └─────────────────┘
```

Сервіс `Migration Control Plane` функціонує в ізольованому адміністративному сегменті мережі (Management VPC) і вимагає суворої взаємної автентифікації TLS (mTLS) та JWT-токенової авторизації з правами `migration:admin`. Кожна дія зі зміни фази або швидкості фонового заповнення атомарно фіксується в незмінному журналі аудиту (англ. *Immutable Audit Log*) із збереженням цифрового підпису оператора, що запобігає несанкціонованому зміщенню прапорців.

---

## 2. Специфікація REST API панелі управління міграцією

Усі адміністративні запити виконуються через HTTPS за протоколом TLS 1.3. Для запобігання дублюванню мутацій при повторних мережевих запитах усі модифікуючі методи вимагають передачі заголовка ідемпотентності `X-Idempotency-Key`.

### 2.1 Отримання поточного стану фази міграції

Ендпоінт надає повну системну картину поточного стану міграційного контуру для зазначеного регіонального кластера, включаючи статус Feature Flags, статистику фонового заповнення та поточні показники розбіжності даних між v1 і v2.

* **HTTP Метод**: `GET`
* **Шлях**: `/api/v2/admin/migration/status`
* **Заголовки**:
  * `Authorization: Bearer <ADMIN_TOKEN>`
  * `X-Client-Region: eu-central-1`
* **Код відповіді**: `200 OK`

```json
{
  "clusterId": "eu-central-1-main",
  "currentPhase": "PHASE_2_READ_SWITCH",
  "previousPhase": "PHASE_1_DUAL_WRITE",
  "phaseTransitionTimestampMs": 1776518400000,
  "pointOfNoReturnPassed": true,
  "flags": {
    "dual_write_enabled": true,
    "read_primary_v2_enabled": true,
    "verification_harness_rate": 0.05,
    "backfill_active": true
  },
  "backfillStats": {
    "totalHomes": 1200000,
    "migratedHomes": 845000,
    "progressPercentage": 70.41,
    "currentRateLimitEps": 500,
    "estimatedCompletionSeconds": 7100
  },
  "driftMetrics": {
    "mismatchRate5m": 0.000002,
    "outboxLagSeconds": 0.12,
    "fallbackToBCount5m": 0
  }
}
```

### 2.2 Зміна фази міграції та перемикання прапорців

Перехід між фазами виконується шляхом відправки підписаного запиту на зміну стану. Сервіс автоматично перевіряє виконання вхідних метричних умов (наприклад, рівень розбіжностей у Parallel Run нижчий за поріг).

* **HTTP Метод**: `POST`
* **Шлях**: `/api/v2/admin/migration/phase`
* **Заголовки**: 
  * `Authorization: Bearer <ADMIN_TOKEN>`
  * `Content-Type: application/json`
  * `X-Idempotency-Key: 9f82a1b4-2104-4c8a-b912-1049281a0b3c`

```json
{
  "targetPhase": "PHASE_2_READ_SWITCH",
  "reason": "mismatch_rate < 0.001% протягом 48 годин у Фазі 1",
  "approvedBy": "architect-lead@digitalhomes.io",
  "overrideChecks": false,
  "config": {
    "dualWriteEnabled": true,
    "readPrimaryV2Enabled": true,
    "backfillRateEps": 500
  }
}
```

**Коди відповідей та обробка помилок**:
* `200 OK`: Фазу успішно переключено. Зміна конфігурації миттєво транслюється на всі регіональні Edge Gateway через Redis Pub/Sub протягом 50 мілісекунд.
* `409 Conflict`: Спроба переходу у Фазу 2 не пройшла автоматичні перевірки готовності (наприклад, `mismatch_rate` вищий за поріг `0.001%` або `outboxLagSeconds > 1.0`).
* `422 Unprocessable Entity`: Спроба відкату у Фазу 0 після перетину Точки Неповернення без встановлення прапорця `overrideChecks: true`.

---

## 3. HTTP/gRPC Заголовки когерентності та гарантії Read-Your-Writes

Для запобігання візуальним фантомним відкатам стану у мобільному застосунку (коли користувач відчинив розумний замок, але Edge-кеш підтягує застарілу версію з лагу матеріалізації) API Gateway та сервіси твіна використовують спеціалізовані заголовки когерентності.

### 3.1 Послідовний сценарій забезпечення когерентності

Повний ланцюг обробки запиту із забезпеченням гарантії Read-Your-Writes складається з чотирьох послідовних кроків:

1. **Запис мутації**: Мобільний застосунок надсилає команду зміни стану (`POST /api/v2/home/device/state`). Сервіс Твіна v2 виконує мутацію, присвоює стану нове монотонне число `versionSeq = 1049` і повертає відповідь із заголовком `X-DH-Min-Version: 1049`.
2. **Збереження версії клієнтом**: Мобільний застосунок зберігає значення `1049` у локальному сховищі для даного `homeId`.
3. **Опитування стану**: При наступному запиті стану (`GET /api/v2/home/state`) застосунок додає заголовок `X-DH-Min-Version: 1049`.
4. **Рішення на шлюзі (Gateway Routing)**: API Gateway вичитує версію з Redis Edge-кешу. Якщо кеш містить версію `1048` (бо подія Kafka ще знаходиться в дорозі матеріалізації), шлюз виконує `Bypass` кешу і робить прямий запит до матеріалізованого представлення Твіна v2, після чого асинхронно оновлює Redis.

### 3.2 Таблиця заголовків когерентності

| Назва заголовка | Тип даних | Напрям | Опис та правила обробки |
| :--- | :--- | :--- | :--- |
| `X-DH-Min-Version` | `uint64` | Клієнт → Gateway | Мінімальна монотонна версія `versionSeq`, яку мусить мати стан для читання. Якщо кеш містить меншу версію, здійснюється bypass кешу напряму до DB v2. |
| `X-DH-Migration-Phase` | `string` | Gateway → Сервіс | Поточна фаза міграції (`PHASE_0` ... `PHASE_3`) для вибору шляху всередині кодового шва `DeviceTwinRepository`. |
| `X-DH-Fallback-Used` | `boolean` | Сервіс → Gateway | Прапорець, який сповіщає, що під час Фази 2 читання з v2 зазнало збою і запит обслуговано з v1 PostgreSQL. |
| `X-DH-Etag` | `string` | Двостронній | Сильний індикатор консистентності стану формата `W/"v<versionSeq>-<hash>"`. |

---

## 4. Специфікація gRPC контрактів міжсервісного зв'язку

Для внутрішньої міжсервісної взаємодії між API Gateway, воркерами Твіна v2 та сервісом `Migration Control Plane` використовується gRPC протокол.

Нижче наведено фрагмент Protobuf-специфікації контракту викликів управління міграцією.

```protobuf
syntax = "proto3";

package dh.migration.v2;

option go_package = "github.com/digitalhomes/proto/migration/v2;migrationv2";

enum MigrationPhase {
  PHASE_UNSPECIFIED = 0;
  PHASE_0_BASELINE = 1;
  PHASE_1_DUAL_WRITE = 2;
  PHASE_2_READ_SWITCH = 3;
  PHASE_3_CONTRACT = 4;
}

message GetStatusRequest {
  string cluster_id = 1;
}

message GetStatusResponse {
  string cluster_id = 1;
  MigrationPhase current_phase = 2;
  bool point_of_no_return_passed = 3;
  uint64 migrated_homes_count = 4;
  double mismatch_rate_5m = 5;
}

service MigrationControlService {
  rpc GetStatus (GetStatusRequest) returns (GetStatusResponse);
}
```

---

## 5. Специфікація метрик спостережливості Prometheus (Drift & Fitness Telemetry)

Моніторинг ерозії та раптового дрейфу коду/даних здійснюється через набір Prometheus-метрики, які збираються сервісом Gateway, воркерами Твіна v2 та автоматичним CI/CD перевірником.

### 5.1 Метрики дрейфу та узгодженості (Drift Metrics)

* `twin_mismatch_total`: Лічильник невирівняних знімків стану між v1 і v2 під час Parallel Run. Збільшення метрики понад 10 за 5 хвилин викликає автоматичне блокування переходу на Фазу 2.
* `outbox_lag_seconds`: Затримка матеріалізації подій Kafka Outbox у Read Model v2. Нормативне значення для здорової системи — менше 0.25 секунди.

```prometheus
# HELP twin_mismatch_total Кількість розбіжностей між станом v1 та v2 під час Parallel Run
# TYPE twin_mismatch_total counter
twin_mismatch_total{home_region="eu-central", field_name="reported_state.temperature"} 12

# HELP outbox_lag_seconds Затримка матеріалізації подій Kafka Outbox у Read Model v2
# TYPE outbox_lag_seconds gauge
outbox_lag_seconds{topic="dh.twin.events.v1", partition="0"} 0.145

# HELP backfill_progress_ratio Прогрес фонового заповнення історичних даних (0.00 - 1.00)
# TYPE backfill_progress_ratio gauge
backfill_progress_ratio{source_db="postgres_v1", target_db="event_store_v2"} 0.7041

# HELP backfill_token_bucket_delay_seconds Час затримки тротлінгу backfill через навантаження P99 Postgres
# TYPE backfill_token_bucket_delay_seconds gauge
backfill_token_bucket_delay_seconds 0.042
```

### 5.2 Метрики ерозії коду та фітнес-функцій (Fitness Metrics)

* `architecture_erosion_violations_total`: Кількість спроб імпорту легасі-модулів v1 у v2-сервісах, зафіксованих у CI/CD.
* `fallback_to_v1_total`: Кількість аварійних повернень до PostgreSQL v1 під час Фази 2 через таймаути v2.

```prometheus
# HELP architecture_erosion_violations_total Кількість зафіксованих ерозійних порушень меж коду в CI/CD
# TYPE architecture_erosion_violations_total counter
architecture_erosion_violations_total{rule_id="LAYER_VIOLATION_V2_V1_INCLUDE", repository="dh-backend-monolith"} 3

# HELP schema_validation_failures_total Кількість відхилених подій через невідповідність JSON Schema
# TYPE schema_validation_failures_total counter
schema_validation_failures_total{topic="dh.twin.events.v1", service="twin-worker"} 0

# HELP fallback_to_v1_total Кількість аварійних звернень до v1 під час Фази 2
# TYPE fallback_to_v1_total counter
fallback_to_v1_total{reason="read_timeout_v2"} 4
```

---

## 6. Протокол узгодження збоїв Dead Letter Queue (DLQ)

Під час асинхронної трансляції подій із Kafka у матеріалізовану модель v2 можливі збої десеріалізації або конфлікти запису. Усі необроблені події перенаправляються в топік `dh.twin.events.dlq.v1`.

### 6.1 Контракт обгортки DLQ повідомлення

```json
{
  "dlqMeta": {
    "originalTopic": "dh.twin.events.v1",
    "partition": 4,
    "offset": 948102,
    "failedAtMs": 1776518920100,
    "exceptionClass": "VersionSequenceMismatchException",
    "errorMessage": "Отримано versionSeq=1042 при поточному стані v2=1045. Подія застаріла.",
    "retryCount": 3
  },
  "originalPayload": {
    "eventId": "evt-7a91b2c4",
    "homeId": "home-8841",
    "deviceId": "lock-01",
    "versionSeq": 1042,
    "etag": "W/\"v1042-a1f9\"",
    "observedAtMs": 1776518910000,
    "payload": {
      "state": { "door": "unlocked" }
    }
  }
}
```

### 6.2 Алгоритм узгодження (Reconciliation Runbook)

1. **Автоматичний випуск (Auto-Replay)**: Якщо причиною DLQ був тимчасовий мережевий таймаут БД (`retryCount < 3`), воркер автоматично повторює спробу запису через `exponential backoff with jitter`.
2. **Конфлікт застарілих версій (`versionSeq <= currentSeq`)**: Подія визнається скинутою (Dropped Stale), інкрементується метрика `dlq_stale_dropped_total`, подія архівується в cold storage.
3. **Критичний конфлікт даних**: Якщо `retryCount >= 3` і помилка належить до категорії десеріалізації, генерується `PagerDuty` сповіщення черговому архітектору, а запис вимагає ручної інспекції через `/api/v2/admin/migration/dlq/replay`.

Ця специфікація діє як єдине нормативне джерело правди для інженерів платформи Digital Homes v2 під час проведення міграційних робіт.
