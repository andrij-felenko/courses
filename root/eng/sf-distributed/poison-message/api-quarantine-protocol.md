# 📋 Специфікація діагностичного конверта карантину та протокол керування інцидентами

Ця специфікація встановлює єдиний міжсервісний стандарт для формування діагностичних конвертів, структури метаданих, протокольних заголовків, кінцевого автомата життєвого циклу та програмних інтерфейсів (REST і gRPC) для ізоляції, аудиту, модифікації та безпечного повторного введення отруйних повідомлень (*Poison Messages*) у розподілених системах обробки подій.

У великих розподілених архітектурах сотні мікросервісів обмінюються повідомленнями через брокери (Apache Kafka, RabbitMQ, AWS SQS/Kinesis, NATS). Коли повідомлення спричиняє детермінований збій, просте перекидання «сирих» байтів у мертву чергу позбавляє інженерів контексту: невідомо, яка саме версія коду впала, який був стектрейс винятку, скільки спроб було здійснено та з якого конкретно зміщення або партиції надійшов дефект. Стандартизований протокол карантину розв'язує цю проблему, перетворюючи кожне ізольоване повідомлення на повноцінний діагностичний артефакт із гарантією збереження аудиторського сліду.

---

## 1. Транспортні заголовки протоколу карантину

Під час перенаправлення дефектного повідомлення з основного контуру в карантинний топік або базу даних, клієнтський супервізор зобов'язаний зберегти оригінальні заголовки продюсера та додати стандартизований блок метаданих із префіксом `X-Quarantine-`:

| Заголовок HTTP / Атрибут брокера | Тип даних | Опис та інженерне призначення |
| :--- | :--- | :--- |
| `X-Quarantine-ID` | `UUIDv4` | Унікальний глобальний ідентифікатор інциденту карантину для трасування. |
| `X-Quarantine-Original-Topic` | `String` | Назва вихідної черги або топіка (`orders-v1`, `payments-stream`). |
| `X-Quarantine-Original-Partition` | `Int32` | Номер партиції (секції) журналу подій, де зафіксовано збій. |
| `X-Quarantine-Original-Offset` | `Int64` | Початкове зміщення (Offset) запису у вихідній партиції для кореляції з логами. |
| `X-Quarantine-Failure-Reason` | `Enum` | Категорія дефекту: `SCHEMA_MISMATCH`, `INVARIANT_VIOLATION`, `RESOURCE_EXHAUSTION`, `RUNTIME_PANIC`, `MAX_RETRIES_EXCEEDED`. |
| `X-Quarantine-Fingerprint` | `Hex` | Криптографічний SHA-256 хеш оригінального тіла (Payload) для дедуплікації сплесків. |
| `X-Quarantine-Attempts` | `Int32` | Точна кількість спроб виконання до моменту остаточної ізоляції. |
| `X-Quarantine-Quarantined-At` | `ISO-8601` | Точний мілісекундний UTC-час потрапляння в карантин (`2026-08-20T14:02:11.450Z`). |
| `X-Quarantine-Host` | `String` | Ідентифікатор вузла/пода (`worker-k8s-pod-89fdc7`), де стався збій. |

---

## 2. Схема діагностичного конверта (Quarantine Envelope)

Діагностичний конверт є самодостатнім контейнером, що містить як оригінальні бінарні дані, так і повну інформацію про причини збою.

### JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "QuarantineEnvelope",
  "type": "object",
  "required": [
    "quarantine_id",
    "original_message_id",
    "original_topic",
    "payload_base64",
    "payload_sha256",
    "failure_reason",
    "exception",
    "status",
    "delivery_attempts",
    "quarantined_at"
  ],
  "properties": {
    "quarantine_id": { "type": "string", "format": "uuid" },
    "original_message_id": { "type": "string" },
    "original_topic": { "type": "string" },
    "original_partition": { "type": "integer" },
    "original_offset": { "type": "integer" },
    "partition_key": { "type": "string" },
    "payload_base64": { "type": "string", "description": "Оригінальні байти повідомлення" },
    "mutated_payload_base64": { "type": ["string", "null"], "description": "Виправлене тіло після тріажу" },
    "payload_sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
    "failure_reason": {
      "type": "string",
      "enum": [
        "SCHEMA_MISMATCH",
        "INVARIANT_VIOLATION",
        "RESOURCE_EXHAUSTION",
        "RUNTIME_PANIC",
        "MAX_RETRIES_EXCEEDED"
      ]
    },
    "exception": {
      "type": "object",
      "required": ["class_name", "message", "stacktrace"],
      "properties": {
        "class_name": { "type": "string" },
        "message": { "type": "string" },
        "stacktrace": { "type": "array", "items": { "type": "string" } }
      }
    },
    "status": {
      "type": "string",
      "enum": ["QUARANTINED", "UNDER_REVIEW", "MUTATED", "REPLAYING", "RESOLVED", "PURGED"]
    },
    "delivery_attempts": { "type": "integer", "minimum": 1 },
    "quarantined_at": { "type": "string", "format": "date-time" },
    "resolved_at": { "type": ["string", "null"], "format": "date-time" },
    "operator_notes": { "type": "string" }
  }
}
```

---

## 3. Кінцевий автомат станів повідомлення в карантині

Життєвий цикл повідомлення з моменту детекції до утилізації описується детермінованим кінцевим автоматом:

```
        ┌──────────────────────────────────────────────┐
        │                                              │
        ▼                                              │
  [QUARANTINED] ──(Блокування на аналіз)──> [UNDER_REVIEW]
                                                  │
                ┌─────────────────────────────────┼────────────────────────────────┐
                │                                 │                                │
        (Патч схеми/коду)                 (Ручна мутація даних)            (Визнано сміттям)
                │                                 │                                │
                ▼                                 ▼                                ▼
       [Ready for Replay]                 [MUTATED]                           [PURGED]
                │                                 │
                └────────────────┬────────────────┘
                                 │
                         (Canary Replay OK)
                                 │
                                 ▼
                           [REPLAYING]
                                 │
                        (Успішний Commit)
                                 │
                                 ▼
                            [RESOLVED]
```

### Семантика та інваріанти переходів:
1. `QUARANTINED`: повідомлення ізольовано автоматичним супервізором і збережено в карантинній базі. Воно очікує на реакцію моніторингу або інженера.
2. `UNDER_REVIEW`: оператор або автоматизований діагностичний агент заблокував запис для інспекції (виставляється тимчасове блокування *lease* на 15 хвилин, щоб запобігти одночасній паралельній правці кількома інженерами).
3. `MUTATED`: інженер відредагував дефектні поля у вихідному тілі (наприклад, замінив неприпустиме значення поля `null` або виправив друкарську помилку в ідентифікаторі валюти). Оригінальне тіло зберігається незмінним у полі `payload_base64` для повного аудиту.
4. `PURGED`: запис визнано неприпустимим сміттям, спамом або шкідливою атакою; він видаляється з черги на повтор зі збереженням запису в журналі безпеки.
5. `REPLAYING`: повідомлення проходить канарейковий або дозований спуск у бойовий контур.
6. `RESOLVED`: оновлений споживач успішно опрацював повідомлення і зафіксував бізнес-транзакцію.

---

## 4. REST та gRPC API керування карантином (Triage & Ops API)

REST та gRPC інтерфейси надають повний набір контрактів для побудови веб-панелей адміністратора (*Admin UI*), CLI-інструментів керування інцидентами та систем автоматизованого виправлення.

### Протокольний контракт gRPC (Protocol Buffers v3)

```protobuf
syntax = "proto3";

package quarantine.v1;

service QuarantineService {
  rpc ListMessages (ListMessagesRequest) returns (ListMessagesResponse);
  rpc GetMessage (GetMessageRequest) returns (QuarantineEnvelope);
  rpc MutatePayload (MutatePayloadRequest) returns (MutatePayloadResponse);
  rpc CanaryReplay (CanaryReplayRequest) returns (CanaryReplayResponse);
  rpc BulkRedrive (BulkRedriveRequest) returns (BulkRedriveResponse);
  rpc PurgeMessage (PurgeMessageRequest) returns (PurgeMessageResponse);
}

message ListMessagesRequest {
  string topic = 1;
  string status = 2;
  string failure_reason = 3;
  int32 limit = 4;
  int32 offset = 5;
}

message ListMessagesResponse {
  int64 total = 1;
  repeated QuarantineEnvelope items = 2;
}

message GetMessageRequest {
  string quarantine_id = 1;
}

message MutatePayloadRequest {
  string quarantine_id = 1;
  bytes new_payload = 2;
  string reason = 3;
  string operator_id = 4;
}

message MutatePayloadResponse {
  string quarantine_id = 1;
  string status = 2;
  string mutated_sha256 = 3;
}

message CanaryReplayRequest {
  string quarantine_id = 1;
  bool dry_run = 2;
}

message CanaryReplayResponse {
  bool success = 1;
  int64 execution_duration_ms = 2;
  string error_message = 3;
}

message BulkRedriveRequest {
  string topic = 1;
  string failure_reason = 2;
  int32 max_rate_per_sec = 3;
}

message BulkRedriveResponse {
  string job_id = 1;
  int64 messages_queued = 2;
}

message PurgeMessageRequest {
  string quarantine_id = 1;
  string reason = 2;
  string operator_id = 3;
}

message PurgeMessageResponse {
  bool purged = 1;
}
```

### REST API Ендпоінти

#### 1. Отримання списку інцидентів
`GET /api/v1/quarantine/messages?status=QUARANTINED&topic=orders-v1&limit=50`

Повертає список заблокованих повідомлень із можливістю фільтрації за вихідним топіком, причиною збою та часовим інтервалом.

**Відповідь (`200 OK`):**
```json
{
  "total": 142,
  "items": [
    {
      "quarantine_id": "7b8f9e61-3a1b-4f9e-a89e-5e72d8a4f109",
      "original_message_id": "msg-882194",
      "original_topic": "orders-v1",
      "failure_reason": "SCHEMA_MISMATCH",
      "payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "delivery_attempts": 3,
      "quarantined_at": "2026-08-20T14:02:11.450Z",
      "status": "QUARANTINED"
    }
  ]
}
```

#### 2. Мутація дефектного тіла повідомлення
`POST /api/v1/quarantine/messages/{quarantine_id}/mutate`

Дозволяє виправити структурні помилки у JSON/Protobuf корисного навантаження безпосередньо в сховищі карантину. Якщо інший інженер паралельно редагує це саме повідомлення, сервер повертає статус `409 Conflict`. Якщо надане нове тіло не відповідає схемі даних, повертається `422 Unprocessable Entity`.

**Запит:**
```json
{
  "mutated_payload_json": {
    "order_id": "ORD-99120",
    "customer_id": 48102,
    "total_amount": 1500.00,
    "currency": "UAH"
  },
  "reason": "Виправлено рядок 'NaN' у полі total_amount на валідне число 1500.00",
  "operator": "andrij.f@team"
}
```

**Відповідь (`200 OK`):**
```json
{
  "quarantine_id": "7b8f9e61-3a1b-4f9e-a89e-5e72d8a4f109",
  "status": "MUTATED",
  "mutated_sha256": "4a5c9e6210f9b3c44298fc1c149afbf4c8996fb92427ae41e4649b934ca49599",
  "updated_at": "2026-08-20T14:15:00Z"
}
```

#### 3. Канарейковий повторний запуск (Dry-Run Replay)
`POST /api/v1/quarantine/messages/{quarantine_id}/canary-replay`

Виконує тестовий прогін повідомлення на ізольованому тестовому воркері без фіксації побічних ефектів або запису в бойові таблиці.

**Відповідь (`200 OK`):**
```json
{
  "success": true,
  "execution_duration_ms": 18,
  "output_state": "ORDER_PROCESSED_SUCCESSFULLY",
  "canary_verdict": "SAFE_TO_REDIVE"
}
```

#### 4. Дозований масовий спуск карантину (Bulk Redrive)
`POST /api/v1/quarantine/bulk-redrive`

Запускає асинхронну фонову задачу дозованого перенаправлення накопичених повідомлень назад у вихідну чергу через алгоритм маркерного кошика (*Token Bucket*), гарантуючи відсутність перевантаження бази даних.

**Запит:**
```json
{
  "filter_topic": "orders-v1",
  "filter_reason": "SCHEMA_MISMATCH",
  "target_queue": "orders-v1",
  "max_rate_per_sec": 50,
  "batch_size": 500
}
```

**Відповідь (`202 Accepted`):**
```json
{
  "job_id": "redrive-job-901",
  "status": "RUNNING",
  "messages_queued": 500,
  "estimated_duration_sec": 10
}
```

---

## 5. Розподілене трасування та прокидання контексту (OpenTelemetry Context Propagation)

Коли повідомлення потрапляє в карантин, воно не повинно розривати розподілений слід трасування (*Distributed Trace*):
1. **Збереження TraceContext:** супервізор вичитує заголовки `traceparent` та `tracestate` стандарту W3C із вхідного повідомлення та зберігає їх у конверті.
2. **Створення Span інциденту:** операція поміщення в карантин формує дочірній спан `quarantine.isolate` з атрибутами `exception.type`, `exception.message`, `exception.stacktrace`.
3. **Кореляція під час Replay:** коли через два тижні оператор виконує redrive повідомлення, новий процес обробки стартує з новим ідентифікатором трасування, але містить посилання `SpanLink` на початковий слід збою, що забезпечує наскрізну прозорість для аудиторів безпеки.

---

## 6. Безпека даних та санітизація чутливої інформації (PII & Secrets Sanitization)

Під час збереження тіла повідомлення та стектрейсу винятку в сховище карантину виникає ризик витоку конфіденційних даних (паролів, номерів банківських карток, токенів авторизації або персональних даних клієнтів):
- **Автоматичне маскування (Data Masking):** супервізор перед збереженням конверта пропускає текстові поля через фільтр санітизації, замінюючи чутливі патерни (наприклад, `cardNumber`, `cvv`, `authorization`) маскованими значеннями `***REDACTED***`.
- **Шифрування в спокої (Encryption at Rest):** таблиці та топіки карантину шифруються за допомогою ключів KMS (AES-256-GCM), гарантуючи, що доступ до дефектних бізнес-даних мають лише авторизовані чергові інженери з аудитом кожного перегляду.
- **Політика збереження та очищення (Retention TTL):** нерозв'язані повідомлення в карантині зберігаються строго визначений час (наприклад, 14 або 30 днів). Після закінчення терміну життя повідомлення автоматично архівуються в холодне сховище або видаляються з фіксацією підсумкового звіту.

---

## 7. Метрики спостережуваності (OpenTelemetry Semantic Conventions)

Для забезпечення повної видимості стану карантину сервіси-споживачі та карантинний менеджер зобов'язані експортувати стандартний набір телеметрії:

- `quarantine.messages.ingress_total` *(Counter)* — сумарна кількість повідомлень, відправлених у карантин (з лейблами `topic`, `failure_reason`, `service`).
- `quarantine.messages.active_count` *(Gauge)* — поточна кількість нерозв'язаних інцидентів у карантинному сховищі.
- `quarantine.messages.oldest_age_seconds` *(Gauge)* — вік найстарішого нерозв'язаного повідомлення в карантині (головний тригер для алертингу на вичерпання бізнес-SLA).
- `quarantine.redrive.success_total` *(Counter)* — кількість успішно відновлених повідомлень під час спуску.
- `quarantine.redrive.failure_total` *(Counter)* — повторні збої під час спуску карантину (слугує тригером аварійної зупинки redrive-задачі).
