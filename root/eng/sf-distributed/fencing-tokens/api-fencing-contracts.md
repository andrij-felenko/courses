# 📋 Специфікація контрактів та інтерфейсів токенів огорожі

Цей довідник визначає формальні протокольні контракти, мережеві структури повідомлень, реляційні й NoSQL схеми даних, а також метрики спостережуваності для реалізації механізму токенів огорожі (англ. *fencing tokens*) у розподілених архітектурах.

У розподілених системах взаємне виключення не може спиратися на довіру до клієнтських процесів або на припущення про синхронізований фізичний час. Будь-яка мутація спільного стану вимагає явного підтвердження повноважень безпосередньо у момент виконання запису. Специфікація стандартизує тристоронній протокол взаємодії: генератор монотонних епох (координатор блокувань), клієнтський агент (воркер) та виконавчий бар'єр валідації (сховище стану).

---

## 1. Протокол сервісу блокувань (Lock Coordinator API)

Сервіс координації блокувань виступає єдиним джерелом монотонного логічного часу та номерів поколінь. Він зобов'язаний гарантувати, що кожна успішна видача замка супроводжується генерацією строго зростаючого 64-бітного числа `token_{n+1} > token_n`.

### Визначення gRPC / Protocol Buffers (v3)

```protobuf
syntax = "proto3";

package distributed.locking.v1;

service LockCoordinator {
  // Захопити новий замок або стати в чергу очікування
  rpc AcquireLock(AcquireLockRequest) returns (AcquireLockResponse);

  // Подовжити строк дії існуючої лізи
  rpc RenewLease(RenewLeaseRequest) returns (RenewLeaseResponse);

  // Добровільно звільнити замок після завершення роботи
  rpc ReleaseLock(ReleaseLockRequest) returns (ReleaseLockResponse);
}

message AcquireLockRequest {
  string resource_id = 1;       // Унікальний ідентифікатор ресурсу (наприклад, "account:48291")
  string client_id   = 2;       // Ідентифікатор клієнта (наприклад, "worker-pod-8b4f")
  uint64 lease_ttl_ms = 3;      // Бажана тривалість лізи в мілісекундах
}

message AcquireLockResponse {
  enum Status {
    STATUS_UNSPECIFIED = 0;
    STATUS_GRANTED     = 1;     // Замок успішно надано
    STATUS_BUSY        = 2;     // Замок утримується іншим клієнтом
    STATUS_REJECTED    = 3;     // Відмовлено через помилку або ліміти
  }

  Status status       = 1;      // Результат обробки запиту
  uint64 fencing_token = 2;     // Монотонний 64-бітний токен огорожі (якщо GRANTED)
  uint64 granted_ttl_ms = 3;    // Фактично наданий час лізи в мс
  int64  server_time_unix_ms = 4; // Час координатора для калібрування
}

message RenewLeaseRequest {
  string resource_id  = 1;
  string client_id    = 2;
  uint64 fencing_token = 3;     // Токен, виданий під час первинного захоплення
  uint64 lease_ttl_ms = 4;
}

message RenewLeaseResponse {
  bool   renewed         = 1;   // Чи вдалося подовжити лізу
  uint64 granted_ttl_ms  = 2;
  string error_reason    = 3;   // "LEASE_ALREADY_EXPIRED", "TOKEN_MISMATCH"
}

message ReleaseLockRequest {
  string resource_id  = 1;
  string client_id    = 2;
  uint64 fencing_token = 3;
}

message ReleaseLockResponse {
  bool success = 1;
}
```

### Семантика обробки запитів координатором

1. **Генерація токена**: Координатор підтримує персистентний атомарний лічильник `token_generator`. Під час кожного виклику `AcquireLock`, коли замок вільний або попередня ліза спливла, виконується операція `token = ++token_generator`. Значення лічильника обов'язково фіксується у розподіленому журналі консенсусу (Raft/Paxos) до відправки відповіді клієнту.
2. **Семантика подовження (`RenewLease`)**: Подовження лізи не змінює значення активного токена, якщо запит надійшов до закінчення дедлайну `lease_deadline_ms` від того самого власника `client_id` із валідним токеном. Якщо дедлайн минув, координатор зобов'язаний відхилити запит із помилкою `LEASE_ALREADY_EXPIRED`, примушуючи клієнта пройти процедуру повного повторного захоплення з отриманням нового токена.
3. **Добровільне звільнення (`ReleaseLock`)**: Якщо клієнт успішно завершив роботу, він надсилає запит на звільнення. Координатор обнуляє поле поточного власника, роблячи ресурс доступним для негайного захоплення іншими претендентами без очікування вичерпання TTL.

---

## 2. Протокол захищеного сховища (Storage Mutation API)

Спільне сховище (база даних, файловий шлюз або мікросервіс стану) виступає виконавчим бар'єром. Воно зобов'язане перевіряти монотонність токена перед застосуванням будь-якої модифікації.

### gRPC Контракт на мутацію стану

```protobuf
syntax = "proto3";

package distributed.storage.v1;

service FencedStorage {
  // Атомарний запис із валідацією токена огорожі
  rpc PutFenced(PutFencedRequest) returns (PutFencedResponse);

  // Читання поточного значення разом із найвищим зафіксованим токеном
  rpc GetFenced(GetFencedRequest) returns (GetFencedResponse);
}

message PutFencedRequest {
  string resource_id   = 1;     // Ключ ресурсу
  bytes  payload       = 2;     // Дані для запису
  uint64 fencing_token = 3;     // Токен огорожі, наданий клієнту координатором
  string idempotency_key = 4;   // Унікальний UUID запиту для захисту від мережевих дублікатів
}

message PutFencedResponse {
  enum FencingStatus {
    FENCING_UNSPECIFIED = 0;
    FENCING_ACCEPTED    = 1;    // Токен дійсний, запис зафіксовано
    FENCING_REJECTED_STALE = 2; // Токен застарілий (T_req < highest_seen)
    FENCING_REPLAY_DUPLICATE = 3; // Повторний запит із тим самим idempotency_key
  }

  FencingStatus status       = 1;
  uint64 highest_token_seen = 2; // Найбільший токен, відомий сховищу
  string error_message       = 3;
}

message GetFencedRequest {
  string resource_id = 1;
}

message GetFencedResponse {
  bytes  payload            = 1;
  uint64 highest_token_seen = 2;
  uint64 version_id         = 3;
}
```

### Інваріанти валідації сховища

Сховище асоціює з кожним ресурсом числове поле `highest_token_seen`, початкове значення якого дорівнює нулю. При отриманні повідомлення `PutFencedRequest` виконується такий алгоритм:

1. **Перевірка ідемпотентності**: якщо `request.idempotency_key` збігається з останнім зафіксованим ключем і `request.fencing_token == highest_token_seen`, сховище повертає `FENCING_REPLAY_DUPLICATE` зі статусом успіху без повторного застосування побічних ефектів.
2. **Перевірка бар'єра огорожі**:
   * Якщо `request.fencing_token >= highest_token_seen`: сховище атомарно записує нові дані `payload`, оновлює `highest_token_seen = request.fencing_token`, зберігає `last_idempotency_key` і повертає `FENCING_ACCEPTED`.
   * Якщо `request.fencing_token < highest_token_seen`: сховище відхиляє запит, не вносячи жодних змін у дані, і повертає статус `FENCING_REJECTED_STALE` разом із поточним значенням `highest_token_seen`.

---

## 3. Реляційні схеми та патерни SQL

У реляційних СКБД (PostgreSQL, MySQL, CockroachDB, SQLite) захист реалізується через умовні оператори модифікації в межах стандартного синтаксису SQL.

### Схема таблиці з метаданими огорожі (PostgreSQL DDL)

```sql
CREATE TABLE IF NOT EXISTS cluster_resources (
    resource_id           VARCHAR(128) PRIMARY KEY,
    payload_data          JSONB NOT NULL,
    highest_fencing_token BIGINT NOT NULL DEFAULT 0,
    last_idempotency_key  VARCHAR(64),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_positive_fencing_token CHECK (highest_fencing_token >= 0)
);

CREATE INDEX idx_cluster_resources_fencing ON cluster_resources (resource_id, highest_fencing_token);
```

### Шаблон атомарного умовного оновлення

Запит оновлення використовує предикат у блоці `WHERE`, що гарантує виконання мутації лише у випадку монотонного зростання номера епохи:

```sql
UPDATE cluster_resources
SET payload_data = :new_payload,
    highest_fencing_token = :token,
    last_idempotency_key = :req_id,
    updated_at = NOW()
WHERE resource_id = :res_id
  AND (highest_fencing_token <= :token)
  AND (last_idempotency_key IS DISTINCT FROM :req_id);
```

### Інтерпретація результатів клієнтським драйвером

Клієнтський код аналізує кількість змінених рядків (`rows affected`):
* Якщо `rows_affected == 1`: операція зафіксована успішно.
* Якщо `rows_affected == 0`: мутація не відбулася. Причиною може бути або спроба застарілого запису від зомбі-процесу, або повторна відправка вже обробленого мережевого пакета. Додаток виконує повторний запит `SELECT highest_fencing_token, last_idempotency_key FROM cluster_resources WHERE resource_id = :res_id` для розрізнення цих двох випадків.

---

## 4. NoSQL та черги повідомлень

### Amazon DynamoDB: вираз умовного запису (Conditional Put)

У DynamoDB валідація здійснюється на стороні розподіленого рушія бази даних через параметр `ConditionExpression`:

```json
{
  "TableName": "ClusterResources",
  "Item": {
    "ResourceId": { "S": "account:48291" },
    "PayloadData": { "S": "{\"balance\": 6500}" },
    "HighestFencingToken": { "N": "35" },
    "LastIdempotencyKey": { "S": "req-9b1d-2b0d" }
  },
  "ConditionExpression": "attribute_not_exists(HighestFencingToken) OR HighestFencingToken <= :req_token",
  "ExpressionAttributeValues": {
    ":req_token": { "N": "35" }
  }
}
```

Якщо інший процес уже встиг записати токен `36`, DynamoDB повертає виняток `ConditionalCheckFailedException`, що трактується клієнтом як відхилення через огорожу.

### Apache Cassandra: легковажні транзакції (LWT / Paxos)

У Cassandra захист реалізується за допомогою директиви `IF` у CQL-запиті, яка ініціює раунд розподіленого консенсусу Paxos між репліками:

```sql
UPDATE cluster_resources
SET payload_data = :new_payload,
    highest_fencing_token = :token
WHERE resource_id = :res_id
IF highest_fencing_token <= :token;
```

Якщо умова не виконується, Cassandra повертає результат `[applied: false]` разом із поточним значенням стовпця `highest_fencing_token`, що сигналізує про виявлення застарілого воркера.

### Apache Kafka: транзакційна огорожа продюсерів (KIP-98)

У протоколі Kafka брокери підтримують стан координатора транзакцій. Кожен заголовок пакета повідомлень містить метадані огорожі:
* `ProducerId` (int64): унікальний числовий ідентифікатор транзакційного клієнта.
* `ProducerEpoch` (int16): монотонний лічильник епохи, що інкрементується координатором при кожній ініціалізації (`InitProducerId`).

Якщо брокер отримує запит `ProduceRequest` з епохою `epoch < current_producer_epoch`, він повертає фатальну помилку `PRODUCER_FENCED`. Клієнтська бібліотека Kafka зобов'язана негайно перевести транзакцію в аварійний стан і викинути виняток `ProducerFencedException`, унеможливлюючи відправку частково сформованих пакетів від старих інстансів воркера.

### Redis: Lua-скрипт атомарної перевірки токена

Якщо як спільне сховище використовується Redis, атомарність операції «перевірити токен і записати нові дані» досягається виконанням Lua-скрипта на стороні сервера:

```lua
-- KEYS[1]: ключ ресурсу даних (наприклад, "data:account:48291")
-- KEYS[2]: ключ метаданих токена (наприклад, "token:account:48291")
-- ARGV[1]: новий токен (fencing_token)
-- ARGV[2]: нові дані (payload)

local current_token = redis.call('GET', KEYS[2])
local req_token = tonumber(ARGV[1])

if not current_token or req_token >= tonumber(current_token) then
    redis.call('SET', KEYS[2], req_token)
    redis.call('SET', KEYS[1], ARGV[2])
    return {1, req_token} -- Успіх: статус 1
else
    return {0, tonumber(current_token)} -- Відхилено: статус 0, поточний максимум
end
```

---

## 5. Специфікація HTTP / REST заголовків

Для веб-сервісів та API-шлюзів передача токенів огорожі стандартизується через спеціалізовані HTTP-заголовки з префіксом `X-Fencing-`.

```http
POST /api/v1/resources/account-48291/mutations HTTP/1.1
Host: api.cluster.internal
Content-Type: application/json
X-Fencing-Token: 35
X-Fencing-Resource-ID: account-48291
X-Idempotency-Key: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
  "balance_cents": 650000,
  "currency": "USD"
}
```

### Формат відповіді при успішній обробці (200 OK):

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Fencing-Status: ACCEPTED
X-Fencing-Highest-Token: 35

{
  "status": "success",
  "resource_id": "account-48291",
  "applied_token": 35
}
```

### Формат відповіді при конфлікті застарілого токена (409 Conflict):

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
X-Fencing-Status: REJECTED_STALE
X-Fencing-Highest-Token: 35

{
  "error": "STALE_FENCING_TOKEN",
  "message": "The provided fencing token 34 is strictly lower than highest accepted token 35",
  "resource_id": "account-48291",
  "rejected_token": 34,
  "highest_token_seen": 35
}
```

---

## 6. Таблиця кодів помилок та матриця станів

| Код помилки | Числовий код gRPC | HTTP статус | Опис причини та рекомендована реакція |
| :--- | :--- | :--- | :--- |
| `STALE_FENCING_TOKEN` | `ABORTED (10)` | `409 Conflict` | Токен запиту строго менший за зафіксований максимум (`T_req < highest_seen`). Клієнт зобов'язаний негайно припинити виконання критичної секції, відкинути локальні результати обчислень і зафіксувати втрату замка. |
| `FENCING_TOKEN_MISMATCH` | `INVALID_ARGUMENT (3)` | `400 Bad Request` | Запит подовження лізи передав токен, не зареєстрований для цього клієнта. Ознака програмної помилки у клієнтській бібліотеці. |
| `LEASE_EXPIRED` | `DEADLINE_EXCEEDED (4)` | `410 Gone` | Ліза випарувалася на координаторі до надходження запиту продовження. Клієнт повинен ініціювати повний цикл повторного захоплення. |
| `IDEMPOTENCY_CONFLICT` | `ALREADY_EXISTS (6)` | `409 Conflict` | Запит передав існуючий `idempotency_key`, але з іншим тілом навантаження (*payload checksum mismatch*). |

---

## 7. Метрики та правила спостережуваності Prometheus

Експлуатація системи з розподіленою огорожею вимагає відстеження телеметрії для раннього виявлення деградації вузлів.

### Опис метрик

```prometheus
# TYPE fencing_stale_rejections_total counter
# HELP fencing_stale_rejections_total Кількість запитів на мутацію, відхилених сховищем через застарілий токен огорожі.
fencing_stale_rejections_total{resource_type="account", reason="stale_token"} 14

# TYPE fencing_token_current_epoch gauge
# HELP fencing_token_current_epoch Поточне максимальне значення токена епохи, згенероване координатором або зафіксоване сховищем.
fencing_token_current_epoch{resource_id="account:48291"} 35

# TYPE fencing_lease_renewals_total counter
# HELP fencing_lease_renewals_total Кількість спроб подовження лізи сторожовим таймером клієнта.
fencing_lease_renewals_total{client_id="worker-pod-8b4f", status="success"} 412
fencing_lease_renewals_total{client_id="worker-pod-8b4f", status="expired"} 1

# TYPE fencing_validation_duration_seconds histogram
# HELP fencing_validation_duration_seconds Тривалість операції атомарної перевірки токена на стороні сховища.
fencing_validation_duration_seconds_bucket{le="0.001"} 18400
fencing_validation_duration_seconds_bucket{le="0.005"} 19250
fencing_validation_duration_seconds_bucket{le="0.010"} 19300
```

### Правила попередження (Prometheus Alert Rules)

```yaml
groups:
  - name: fencing_alerts
    rules:
      - alert: FencingStaleWriteDetected
        expr: increase(fencing_stale_rejections_total[5m]) > 0
        for: 0m
        labels:
          severity: warning
        annotations:
          summary: "Зомбі-клієнт здійснив спробу застарілого запису"
          description: "Сховище відхилило {{ $value }} застарілих запитів за останні 5 хвилин. Необхідно перевірити тривалість пауз GC або стабільність мережі воркерів."

      - alert: FencingLeaseExpirationRateHigh
        expr: rate(fencing_lease_renewals_total{status="expired"}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Висока частота передчасного спливання ліз"
          description: "Понад 5% спроб продовження оренди завершуються таймаутом. Клієнти не встигають надсилати запити через зависання або перевантаження CPU."
```

### Інженерний регламент реагування на інциденти (Runbook)

1. **Спрацьовування `FencingStaleWriteDetected`**:
   * Отримати `client_id` та `rejected_token` з журналів сховища.
   * Перевірити логи відповідного воркера на наявність тривалих пауз GC (`jstat -gcutil`, Go GC traces або `runtime/pprof`).
   * Перевірити показники завантаження CPU хоста (`iowait`, `steal time` у віртуалізованих середовищах).
   * Якщо воркер деградував, перезапустити інстанс або налаштувати ліміти пам'яті контейнера.

2. **Спрацьовування `FencingLeaseExpirationRateHigh`**:
   * Перевірити мережеву затримку (RTT) між пулом воркерів та кластером координатора замків.
   * Збільшити інтервал TTL лізи або зменшити частоту подовження `T_renew = TTL / 4` для надання додаткового запасу часу на мережеві повтори.
