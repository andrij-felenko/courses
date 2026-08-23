# 🔌 Компонентна архітектура вихідного ідемпотентного шлюзу

Вихідний ідемпотентний шлюз (англ. *Outbound Idempotency Gateway*) — це спеціалізований архітектурний компонент сервісу, який ізолює доменну логіку від мережевої невизначеності й обертає всі вихідні виклики до зовнішніх API (платіжних провайдерів, push-сервісів, SMS-шлюзів, сторонніх вебхуків). Головне призначення компонента — надати доменній логіці гарантію «виконати дію не більше й не менше ніж один раз» (exactly-once semantics на рівні побічного ефекту) навіть за умов обривів мережі, таймаутів та аварійних перезавантажень систем.

## Загальна схема та шари компонента

Вихідний шлюз не є просто декоратором над HTTP-клієнтом. Це повноцінна підсистема, що складається з чотирьох взаємопов'язаних шарів:

1. **Шар генерації та валідації ключів (Key Engine)**:
   - Обчислює детермінований ідентифікатор `Idempotency-Key` на основі локального ідентифікатора сутності (`order_id`, `notification_uuid`).
   - Генерує SHA-256 відбиток корисного навантаження (Payload Fingerprint) для контролю незмінності параметрів запиту при ретраях.

2. **Транзакційний журнал вихідних дій (Outbound Log / Outbox Store)**:
   - Локальне персистентне сховище (найчастіше таблиця в базовій реляційній СУБД сервісу), яке записує намір виконати вихідну дію атомарно з локальною ACID-транзакцією.
   - Забезпечує зберігання станів виконання, лічильників спроб та кешованих відповідей від зовнішніх систем.

3. **Планувальник та виконавець спроб (Retry Executor & Backoff Scheduler)**:
   - Фоновий воркер або асинхронний пул потоків, що вичитує невиконані записи з журналу та здійснює мережеві HTTP/gRPC виклики.
   - Реалізує алгоритм затримки **Exponential Backoff із випадковим дрожанням (Jitter)** для запобігання проблемам каскадного перевантаження (Thundering Herd Problem).

4. **Детектор мережевих станів та інтерпретатор відповідей (Response Classifier)**:
   - Класифікує результати виклику за трьома категоріями: остаточний успіх, тимчасовий збій (потрібен ретрай) та незворотна помилка домену (ретрай заборонено).

---

## Структура таблиці вихідного журналу (Outbox Schema)

Для забезпечення гарантії збереження наміру навіть при падінні процесу, шлюз використовує локальну таблицю в СУБД. Еталонна схема таблиці `outbound_idempotency_log` має такий вигляд:

```sql
CREATE TABLE outbound_idempotency_log (
    id BIGSERIAL PRIMARY KEY,
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    payload_hash VARCHAR(64) NOT NULL,
    target_url VARCHAR(1024) NOT NULL,
    http_method VARCHAR(10) NOT NULL DEFAULT 'POST',
    request_headers JSONB NOT NULL,
    request_body JSONB NOT NULL,
    
    state VARCHAR(32) NOT NULL DEFAULT 'PENDING', -- PENDING, IN_FLIGHT, COMPLETED, FAILED_FATAL
    response_status INT NULL,
    response_headers JSONB NULL,
    response_body TEXT NULL,
    
    retry_count INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 5,
    next_retry_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_outbound_pending ON outbound_idempotency_log (state, next_retry_at) 
WHERE state IN ('PENDING', 'IN_FLIGHT');
```

Атомарність досягається тим, що при виконанні доменної операції (наприклад, створення замовлення мешканцем) бізнес-код виконує `INSERT INTO orders` та `INSERT INTO outbound_idempotency_log` в **одній локальній ACID-транзакції**. Якщо створення замовлення відкочується, вихідний виклик не буде створено взагалі.

---

## Матриця станів та переходами (State Machine)

Кожен вихідний виклик усередині шлюзу проходить чітко визначений життєвий цикл станів:

```
[Початок] ──(DB Tx)──> [PENDING] ──(Worker Pick)──> [IN_FLIGHT]
                                                       │
         ┌──────────────────────┬──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼                      ▼
  (HTTP 200/201)        (Timeout / 5xx)         (HTTP 409 Conflict)    (HTTP 400/422)
         │                      │                      │                      │
         ▼                      ▼                      ▼                      ▼
    [COMPLETED] ──(Max Retries Exceeded)──> [FAILED_RETRYABLE]          [FAILED_FATAL]
```

### Деталізація переходів станів:

1. **`PENDING` → `IN_FLIGHT`**:
   Воркер вичитує записи зі станом `PENDING`, у яких `next_retry_at <= NOW()`, за допомогою блокування `SELECT ... FOR UPDATE SKIP LOCKED`. Це гарантує, що кілька паралельних воркерів не візьмуть одне й те саме завдання. Стан атомарно змінюється на `IN_FLIGHT`.

2. **`IN_FLIGHT` → `COMPLETED`**:
   Отримано відповідь `HTTP 200 OK` або `HTTP 201 Created`. Шлюз записує у журнал `response_status`, `response_headers` та `response_body`, оновлює стан на `COMPLETED`. Доменну сагу можна продовжувати.

3. **`IN_FLIGHT` → `IN_FLIGHT` (Retry Schedule)**:
   Отримано `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout` або відбувся мережевий таймаут TCP. Шлюз **не змінює `idempotency_key`**, збільшує `retry_count` на 1, вираховує нове значення `next_retry_at` за формулою:
   
   `backoff = min(max_backoff, base_backoff * 2^(retry_count) + random_jitter)`
   
   Запис залишається в стані `PENDING` або `IN_FLIGHT` до настання `next_retry_at`.

4. **`IN_FLIGHT` → `IN_FLIGHT` (Conflict Wait)**:
   Отримано `HTTP 409 Conflict` або `HTTP 429 Too Many Requests`. Зовнішній сервіс повідомляє, що попередній виклик із цим ключем ще очікує виконання на його боці. Шлюз зчитує заголовок `Retry-After` (якщо є) або застосовує паузу в 2-5 секунд, залишаючи заголовок `Idempotency-Key` незмінним.

5. **`IN_FLIGHT` → `FAILED_FATAL`**:
   Отримано помилку валідації `HTTP 400 Bad Request`, `HTTP 401 Unauthorized` або `HTTP 422 Unprocessable Entity (Payload Mismatch)`. Повтор таких запитів позбавлений сенсу. Запис позначається як `FAILED_FATAL`, воркер зупиняє ретраї й надсилає сповіщення оператору або в Dead Letter Queue (DLQ).

---

## Обробка кешованих відповідей та фільтрація заголовків

Коли зовнішній провайдер повертає кешовану відповідь (відтворення з `Idempotent-Replay: true`), шлюз мусить коректно передати її доменному сервісу.

Однак не всі HTTP-заголовки від зовнішнього API можна безпечно кешувати й повертати доменному коду. Шлюз ділить заголовки відповіді на дві категорії:

- **Заголовки, що кешуються (Preserved Headers)**: `Content-Type`, `Content-Language`, `X-Request-Id`, `Stripe-Version`, бізнес-ідентифікатори провайдера.
- **Заголовки, що відкидаються (Stripped Headers)**: Transport-specific заголовки: `Set-Cookie`, `Connection`, `Transfer-Encoding`, `Keep-Alive`, `Date`, `Server`. Кешування цих заголовків може призвести до збоїв у HTTP-клієнті або витоку сесійних маркерів.

---

## Конкуренція та захист від гонки (Concurrency & Lock Contention)

У високонавантажених сервісах виникає проблема: що робити, якщо два події в домені згенерували два вихідні виклики з однаковим дедуп-ключем майже одночасно?

Вихідний шлюз вирішує це на двох рівнях:

1. **Локальний рівень (Local Mutex / DB Constraint)**:
   Унікальний індекс `UNIQUE (idempotency_key)` у таблиці `outbound_idempotency_log` запобігає створенню двох записів із однаковим ключем у локальній БД. Другий спроба створити такий самий запис завершиться помилкою унікальності індексу на рівні SQL-транзакції.

2. **Мережевий рівень (Distributed Lock / Remote In-Flight)**:
   Якщо два воркери на різних вузлах кластера намагаються відправити запит паралельно, зовнішнє API відхилить другий запит кодом `409 Conflict`. Шлюз-відправник перехопить `409` і переведе другий воркер у режим очікування, поки перший воркер не завершить виклик і не отримає `200 OK`.

Завдяки цьому компонентна архітектура вихідного шлюзу повністю закриває всі можливі траєкторії мережевих та доменних збоїв, перетворюючи ненадійне HTTP-середовище на прозорий і надійний канал зв'язку.
