# 📋 Специфікація API-контрактів та схем подій PayFlow

Ця вставка містить вичерпну специфікацію gRPC-інтерфейсів, Protobuf-схем міжсервісного обміну, форматів асинхронних подій Transactional Outbox та публічного REST API для високонавантаженої платформи еквайрингу PayFlow. Інтерфейси розроблено з урахуванням суворих вимог до зворотної сумісності, мінімальної серіалізаційної латентності (p99 < 200 мс) та гарантій фінансової консистентності.

---

## 1. Внутрішній gRPC-контракт Ledger Engine (`ledger.v1`)

Сервіс фінансового обліку (`Ledger Node`) надає ізольований gRPC API для виконання бухгалтерського подвійного запису (double-entry bookkeeping). Оскільки цей вузол обробляє баланси торговців та накопичені комісії платформи, всі RPC-методи є суворо детермінованими, вимагають атрибутів ідемпотентності та унікальних ідентифікаторів транзакцій.

### Протокольний контракт Protobuf (`payflow/ledger/v1/ledger.proto`)

```protobuf
syntax = "proto3";

package payflow.ledger.v1;

option go_package = "payflow/ledger/v1;ledgerv1";
option cpp_generic_services = true;

// Сервіс фінансового обліку та управління балансами
service LedgerService {
  // Запис фінансової транзакції за методом подвійного запису
  rpc RecordTransaction(RecordTransactionRequest) returns (RecordTransactionResponse);

  // Отримання поточного балансу рахунку торговця
  rpc GetAccountBalance(GetAccountBalanceRequest) returns (GetAccountBalanceResponse);
}

// Типи валют, що підтримуються платформою
enum Currency {
  CURRENCY_UNSPECIFIED = 0; // Заборонене значення за замовчуванням
  CURRENCY_USD = 1;         // Долар США
  CURRENCY_EUR = 2;         // Євро
  CURRENCY_GBP = 3;         // Фунт стерлінгів
  CURRENCY_UAH = 4;         // Гривня
}

// Категорія системного або торгівельного рахунку
enum AccountType {
  ACCOUNT_TYPE_UNSPECIFIED = 0;
  ACCOUNT_TYPE_MERCHANT_SETTLEMENT = 1; // Рахунок виплат торговцю
  ACCOUNT_TYPE_SYSTEM_COMMISSION = 2;   // Рахунок системної комісії PayFlow
  ACCOUNT_TYPE_CUSTOMER_HOLD = 3;       // Тимчасовий страховий депозит
}

// Структура грошової суми у фіксованій точці
message Money {
  Currency currency = 1;
  // Сума у найменших неподільних одиницях валюти (наприклад, центи для USD/EUR, копійки для UAH)
  int64 units = 2;
}

// Позиція в журналі подвійного запису
message LedgerEntry {
  string account_id = 1;
  AccountType account_type = 2;
  // Напрямок руху коштів: true - дебет (+), false - кредит (-)
  bool is_debit = 3;
  Money amount = 4;
}

// Запит на створення транзакції подвійного запису
message RecordTransactionRequest {
  // Унікальний ключ ідемпотентності операції (генериться Saga Orchestrator)
  string idempotency_key = 1;
  string merchant_id = 2;
  string charge_id = 3;
  
  // Елементи подвійного запису: сума всіх дебетів повинна дорівнювати сумі всіх кредитів
  repeated LedgerEntry entries = 4;
  
  // Додаткові метадані операції
  map<string, string> metadata = 5;
  int64 timestamp_utc_ms = 6;
}

// Відповідь сервісу фінансового обліку
message RecordTransactionResponse {
  string transaction_id = 1;
  enum Status {
    STATUS_UNSPECIFIED = 0;
    STATUS_COMMITTED = 1;                 // Запис успішно зафіксовано в ACID-транзакції
    STATUS_REJECTED_INSUFFICIENT_FUNDS = 2; // Відхилено через відсутність доступного балансу
    STATUS_DUPLICATE_IGNORED = 3;          // Повторний запит із тим самим ключем ідемпотентності
  }
  Status status = 2;
  int64 committed_at_utc_ms = 3;
}

// Запит стану балансу
message GetAccountBalanceRequest {
  string merchant_id = 1;
  string account_id = 2;
}

// Відповідь із деталізацією доступних та заблокованих коштів
message GetAccountBalanceResponse {
  string account_id = 1;
  Money available_balance = 2;
  Money pending_hold_balance = 3;
  int64 as_of_timestamp_utc_ms = 4;
}
```

### Деталізація полів та гарантії цілісності

* `units` (у структурі `Money`): Грошові суми свідомо представлені цілим 64-бітним числом (`int64`) у найменших неподільних одиницях валюти (центи для USD/EUR, копійки для UAH). Використання чисел із плаваючою крапкою (`float`, `double`) суворо заборонено через ризик накопичення округлювальних помилок стандарту IEEE 754 під час багаторазового додавання та віднімання фінансових часток.
* `idempotency_key` (у структурі `RecordTransactionRequest`): Обов'язковий UUIDv4, який гарантує, що при повторній відправці запису через мережевий розрив або затримку gRPC `Ledger Node` не здійснить повторне списання або зарахування коштів. Сервіс перевіряє унікальність ключа в унікальному індексі PostgreSQL і у разі збігу повертає статус `STATUS_DUPLICATE_IGNORED` із раніше обчисленим `transaction_id`.
* `entries`: Масив `LedgerEntry` має задовольняти базовому інваріанту подвійного запису. Перед відкриттям ACID-транзакції `Ledger Engine` підсумовує `units` для дебетових та кредитових записів у розрізі кожної валюти. Якщо `sum(Debits) != sum(Credits)`, запит відхиляється на стадії валідації з кодом gRPC `INVALID_ARGUMENT`.

### Відображення помилок gRPC на коди HTTP

Під час взаємодії через gRPC між внутрішніми вузлами та API Gateway статуси помилок транслюються за канонічною матрицею відповідності:

* `gRPC OK (0)` → `HTTP 200 OK` / `HTTP 201 Created`
* `gRPC INVALID_ARGUMENT (3)` → `HTTP 400 Bad Request` (помилка у форматі полів або порушення інваріанту)
* `gRPC DEADLINE_EXCEEDED (4)` → `HTTP 504 Gateway Timeout` (перевищено часовий ліміт виконання у 500 мс)
* `gRPC NOT_FOUND (5)` → `HTTP 404 Not Found` (запитаний транзакційний рахунок відсутній)
* `gRPC ALREADY_EXISTS (6)` → `HTTP 409 Conflict` (конфлікт ключів у базі даних)
* `gRPC RESOURCE_EXHAUSTED (8)` → `HTTP 429 Too Many Requests` (перевищено квоту транзакцій торговця)
* `gRPC UNAUTHENTICATED (16)` → `HTTP 401 Unauthorized` (невалідний mTLS-сертифікат або JWT)

---

## 2. Схеми подій Transactional Outbox та Kafka Topics

Після успішної фіксації транзакції списання у базі даних `Payment Core` записує подійний слід у таблицю `outbox_events`. Процес-релей транслює ці записи у шину подій Apache Kafka.

### 1. Топік Kafka: `payflow.charges.v1`
* **Ключ партиціонування (Partition Key):** `merchant_id`. Забезпечує сувору послідовність обробки всіх подій конкретного торговця у межах однієї партиції Kafka, унеможливлюючи порушення порядку (out-of-order execution) при паралельній обробці.
* **Заголовки Kafka (Kafka Record Headers):**
  * `x-payflow-trace-id`: Унікальний ID трасування OpenTelemetry для наскрізного простеження запиту.
  * `x-payflow-event-id`: UUIDv4 події для дедуплікації на боці споживача.
  * `x-payflow-schema-version`: Версія Protobuf-схеми (поточна = `1`).
  * `x-payflow-timestamp`: UTC timestamp публікації у мілісекундах.

```protobuf
syntax = "proto3";

package payflow.events.v1;

import "google/protobuf/timestamp.proto";

enum ChargeStatus {
  CHARGE_STATUS_UNSPECIFIED = 0;
  CHARGE_STATUS_PENDING = 1;
  CHARGE_STATUS_SUCCEEDED = 2;
  CHARGE_STATUS_FAILED = 3;
  CHARGE_STATUS_REFUNDED = 4;
}

message ChargeSucceededEvent {
  string event_id = 1;              // Унікальний UUID події
  string event_type = 2;            // "charge.succeeded"
  int32 schema_version = 3;         // Версія схеми (поточна = 1)

  string charge_id = 4;             // Ідентифікатор платежу
  string merchant_id = 5;           // Ідентифікатор торговця
  string idempotency_key = 6;       // Первинний ключ замовлення

  int64 amount_cents = 7;           // Сума у центах
  string currency = 8;              // Валюта ("USD", "EUR")
  
  string payment_method_type = 9;   // "card", "apple_pay", "sepa"
  string last4 = 10;                // Останні 4 цифри картки

  ChargeStatus status = 11;
  google.protobuf.Timestamp occurred_at = 12; // Час події у UTC
  
  map<string, string> merchant_metadata = 13;
}
```

### 2. JSON Schema для асинхронних Webhook-повідомлень

Вузол `Webhook Worker Pool` зчитує події з Kafka, трансформує їх у JSON-формат та надсилає HTTP POST запит на `webhook_url` торговця.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PayFlowWebhookPayload",
  "type": "object",
  "required": [
    "id",
    "object",
    "api_version",
    "created",
    "type",
    "data"
  ],
  "properties": {
    "id": {
      "type": "string",
      "description": "Унікальний ідентифікатор події сповіщення",
      "example": "evt_1N2x3y4Z5a6B7c8D"
    },
    "object": {
      "type": "string",
      "enum": ["event"]
    },
    "api_version": {
      "type": "string",
      "description": "Версія API, під яку згенеровано структуру",
      "example": "2026-08-01"
    },
    "type": {
      "type": "string",
      "enum": [
        "charge.succeeded",
        "charge.failed",
        "charge.refunded",
        "payout.paid"
      ]
    },
    "created": {
      "type": "integer",
      "description": "UTC timestamp виникнення події у секундах Unix",
      "example": 1787049600
    },
    "data": {
      "type": "object",
      "required": ["object"],
      "properties": {
        "object": {
          "type": "object",
          "required": [
            "id",
            "merchant_id",
            "amount",
            "currency",
            "status",
            "idempotency_key"
          ],
          "properties": {
            "id": { "type": "string", "example": "ch_3M4v5w6X7y8Z" },
            "merchant_id": { "type": "string", "example": "mer_987654321" },
            "amount": { "type": "integer", "example": 4500 },
            "currency": { "type": "string", "example": "USD" },
            "status": { "type": "string", "example": "succeeded" },
            "idempotency_key": { "type": "string", "example": "order_ref_10024" }
          }
        }
      }
    }
  }
}
```

---

## 3. Публічний Зовнішній REST/OpenAPI Контракт

Зовнішні сервери торговців та мобільні клієнти взаємодіють із периферійним API Gateway через захищений HTTPS REST API.

### Ендпоінт Створення Платежу: `POST /v1/charges`

#### Заголовки Запиту (Request Headers)
* `Authorization`: `Bearer sec_key_live_9f8a...` (API Ключ торговця)
* `Idempotency-Key`: `string` (Обов'язковий унікальний рядок, наприклад UUIDv4)
* `Content-Type`: `application/json`

#### Тіло Запиту (Request Body)
```json
{
  "amount": 4500,
  "currency": "USD",
  "source": "tok_visa_debit_4444",
  "description": "Оплата замовлення №10024 у маркетплейсі",
  "statement_descriptor": "PAYFLOW*STORE10024",
  "metadata": {
    "order_id": "10024",
    "customer_email": "user@example.com"
  }
}
```

#### Успішна Відповідь: `201 Created`
```json
{
  "id": "ch_3M4v5w6X7y8Z",
  "object": "charge",
  "amount": 4500,
  "amount_captured": 4500,
  "currency": "USD",
  "paid": true,
  "status": "succeeded",
  "idempotency_key": "order_ref_10024",
  "created": 1787049600,
  "livemode": true,
  "payment_method": {
    "type": "card",
    "card": {
      "brand": "visa",
      "last4": "4242",
      "exp_month": 12,
      "exp_year": 2028
    }
  },
  "failure_code": null,
  "failure_message": null
}
```

#### Заголовки Відповіді для Контролю Лімітів (Rate Limit Headers)
При кожній відповіді API Gateway повертає поточний стан квот торговця:
* `X-RateLimit-Limit`: `1000` (дозволена кількість запитів на хвилину)
* `X-RateLimit-Remaining`: `984` (залишок запитів у поточному вікні)
* `X-RateLimit-Reset`: `1787049660` (Unix-час скидання вікна)

#### Стандарт Пагінації Списків Ресурсів (`GET /v1/charges`)
Для отримання списку транзакцій використовується курсорна пагінація за ідентифікатором запису (`starting_after`), що унеможливлює проблему зсуву елементів (offset shift), притаманну традиційній пагінації `LIMIT/OFFSET` при високій інтенсивності нових записів:

```http
GET /v1/charges?limit=25&starting_after=ch_3M4v5w6X7y8Z HTTP/1.1
Host: api.payflow.com
Authorization: Bearer sec_key_live_9f8a...
```

Відповідь повертає об'єкт списку із можливістю переходу до наступної сторінки:

```json
{
  "object": "list",
  "data": [
    { "id": "ch_4N5w6x7Y8z9A", "amount": 1200, "status": "succeeded" }
  ],
  "has_more": true
}
```

#### Канонічна Форма Помилки (API Error Format — RFC 7807)
У разі помилки відмовленої транзакції або невалідного запиту API повертає структуру за стандартом RFC 7807 (Problem Details):

```json
{
  "type": "https://api.payflow.com/v1/errors/card_declined",
  "title": "Card Declined",
  "status": 402,
  "code": "card_declined",
  "decline_code": "insufficient_funds",
  "detail": "Картка була відхилена банківським емітентом через недостатність коштів на рахунку покупця.",
  "request_id": "req_88f9a0c1e23",
  "doc_url": "https://docs.payflow.com/errors/card_declined"
}
```

---

## 4. Правила Версіонування та Еволюції Схем

### 1. Правило збереження нумерації полів у Protobuf
У Protobuf-схемах видалення полів заборонено. При виведенні поля з експлуатації воно позначається як `reserved`, а його тег нумерації більше ніколи не використовується:

```protobuf
message LedgerEntry {
  reserved 5, 8 to 10;
  reserved "legacy_tax_code", "obsolete_flag";
}
```

### 2. Двоетапний паттерн розширення контракту (Expand-Contract Pattern)
При зміні контрактів між сервісами застосовується трифазна міграція:
1. **Фаза розширення (Expand):** Нове поле додається у Protobuf як `optional`. Сервіси-виробники продовжують писати у старі поля, але починають дублювати дані у нове поле.
2. **Фаза адаптації (Migrate):** Сервіси-споживачі оновлюються для читання з нового поля із фолбеком на старе поле.
3. **Фаза стиснення (Contract):** Старе поле позначається як `deprecated`. Після повного переходу всіх споживачів старе поле переводиться у стан `reserved`.

### 3. Валідація зворотної сумісності у CI/CD
Кожна зміна `.proto` файлів у Git проходить автоматичну перевірку у CI-пайплайні за допомогою інструменту `buf breaking`:

```bash
buf breaking --against '.git#branch=main'
```

Якщо PR містить руйнівні зміни (зміна тегів, зміна типів даних або видалення enum-значень), збірка блокується до виправлення порушення.

---

## 5. Безпека Webhook-доставки та Захист від Підробки

Вузол `Webhook Dispatcher` підписує кожен вихідний HTTP POST запит криптографічним HMAC-SHA256 підписом.

### Формат заголовка підпису:
```http
X-PayFlow-Signature: t=1787049600,v1=9f8a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a
```

### Алгоритм розрахунку підпису на боці торговця:
1. Витягнути значення `t` (timestamp) та `v1` (HMAC hex) із заголовка `X-PayFlow-Signature`.
2. Перевірити, що різниця між поточним часом та `t` не перевищує 300 секунд (захист від атак повторного відтворення — Replay Attacks).
3. Сформувати підписний рядок: `signed_payload = timestamp + "." + request_body_raw`.
4. Обчислити `HMAC-SHA256(signed_payload, merchant_webhook_secret)`.
5. Порівняти обчислений хеш із отриманим `v1` за допомогою алгоритму порівняння зі сталим часом (constant-time comparison) для уникнення таймінгових атак (Timing Attacks).
