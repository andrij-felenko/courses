# 📋 Специфікація контракту лагу read-model

Ця специфікація визначає машинний протокол взаємодії між клієнтськими застосунками, командними сервісами, шлюзами запитів та сховищами моделей читання (Read Models). Вона стандартизує структуру HTTP-заголовків, формат повідомлень gRPC, семантику рівнів узгодженості, правила маршрутизації деградованих запитів та коди помилок у разі порушення бюджету свіжості даних.

Без формалізованого контракту клієнтські інтерфейси та зовнішні інтеграційні системи не мають інструментів для вираження вимог щодо актуальності даних. Це призводить до непередбачуваних помилок `404 Not Found`, читання застарілих балансів і повторного надсилання дублюючих транзакцій.

## 1. Модель рівнів узгодженості (Consistency Levels)

Клієнтський запит може явно визначати бажаний рівень узгодженості для кожної операції читання через HTTP-заголовок `X-Consistency-Level` або відповідне поле gRPC-метаданих:

| Рівень (`enum`) | Семантика виконання | Поведінка шлюзу читання | Припустимий лаг |
| :--- | :--- | :--- | :--- |
| `EVENTUAL` | Клієнт погоджується на будь-який доступний стан моделі читання | Негайне читання з денормалізованого сховища без блокувань | Не обмежений (`0 .. ∞`) |
| `BOUNDED_STALENESS` | Дані не повинні бути старішими за вказаний часовий інтервал `T_max` | Перевірка метрики лагу; якщо `Lag > T_max` — перемикання або відхилення | `Lag ≤ Max-Staleness-Ms` |
| `READ_YOUR_WRITES` | Відповідь гарантовано містить зміни, зафіксовані вказаним версійним токеном | Очікування наздоганяння проєкції до версії `v_req` або пряме читання з первинної бази | `v_read ≥ v_required` |
| `MONOTONIC_READ` | Стан не може бути старішим за версію, яку клієнт уже бачив раніше в цій сесії | Перевірка клієнтського водяного знака сесії (`Session-Watermark`) | `v_read ≥ v_session` |
| `STRONG` | Читання тільки з первинного джерела правди (Write Model Primary DB) | Повний обхід моделі читання, прямий запит до транзакційного сховища | Нульовий (`Lag = 0`) |

## 2. Специфікація HTTP-заголовків запиту

При виконанні операцій `GET`, `HEAD` або `OPTIONS` клієнт передає набір службових метаданих:

### `X-Required-Version`
- **Тип:** 64-бітне беззнакове ціле число або складений рядок ідентифікатора журналу (наприклад, `partition:offset` або `LSN`).
- **Призначення:** Визначає мінімально необхідну версію стану сутності, яку вимагає клієнт для забезпечення контракту `READ_YOUR_WRITES`.
- **Семантика:** Якщо поточний водяний знак обробки проєкції менший за це число, шлюз зобов'язаний призупинити відповідь на час очікування або виконати аварійний обхід.
- **Приклад:** `X-Required-Version: 88412`

### `X-Max-Staleness-Ms`
- **Тип:** Ціле додатне число (мілісекунди).
- **Призначення:** Гранично допустимий фізичний лаг моделі читання для контракту `BOUNDED_STALENESS`.
- **Семантика:** Якщо за даними синтетичного маркерного пульсу проєкція відстає від первинного джерела більше ніж на `X-Max-Staleness-Ms`, запит не може бути виконаний з кешу чи денормалізованого сховища без явного дозволу на деградацію.
- **Приклад:** `X-Max-Staleness-Ms: 250`

### `X-Max-Wait-Ms`
- **Тип:** Ціле додатне число (мілісекунди).
- **Призначення:** Максимальний бюджет часу, який шлюз запитів має право витратити на очікування наздоганяння проєкції (`Wait-for-Version`), перш ніж перемкнутися на резервний контур або повернути помилку клієнту.
- **Значення за замовчуванням:** `100 мс`.
- **Приклад:** `X-Max-Wait-Ms: 50`

### `X-Session-Watermark`
- **Тип:** 64-бітне беззнакове число.
- **Призначення:** Останній відомий клієнту номер версії в межах поточної користувацької сесії (для контракту `MONOTONIC_READ`). Запобігає ситуаціям «подорожі назад у часі» при балансуванні між різними репліками моделі читання.
- **Приклад:** `X-Session-Watermark: 88410`

### `X-Allow-Degraded`
- **Тип:** Булеве значення (`true` / `false`).
- **Призначення:** Дозволяє повернення застарілого стану із позначкою деградації у випадку, коли проєкція відстає від контракту, а первинна транзакційна база перевантажена або захищена запобіжником (circuit breaker).
- **Значення за замовчуванням:** `false`.
- **Приклад:** `X-Allow-Degraded: true`

## 3. Специфікація HTTP-заголовків відповіді

Сервери командного контуру та контуру читання формують стандартизовані метадані у відповідях для забезпечення наскрізного простеження лагу.

### Заголовки відповідей командного контуру (POST / PUT / PATCH / DELETE):
- **`X-Causal-Token`:** Токен версії транзакції або зміщення в журналі подій. Клієнт зобов'язаний зберегти цей токен у локальному сховищі сесії.
  *Приклад:* `X-Causal-Token: 88412`
- **`X-Commit-Timestamp`:** ISO-8601 мітка часу фіксації транзакції на первинному вузлі-лідері.
  *Приклад:* `X-Commit-Timestamp: 2026-08-20T14:32:01.104Z`
- **`X-Event-Partition`:** Номер партиції брокера повідомлень, у яку було записано подію зміни стану.
  *Приклад:* `X-Event-Partition: 4`

### Заголовки відповідей контуру читання (GET / HEAD):
- **`X-Read-Model-Version`:** Фактична версія агрегату або останнє зафіксоване зміщення проєкції, на основі якого зібрано відповідь.
  *Приклад:* `X-Read-Model-Version: 88412`
- **`X-Read-Model-Lag-Ms`:** Фактичний фізичний лаг проєкції в мілісекундах на момент генерації відповіді.
  *Приклад:* `X-Read-Model-Lag-Ms: 14`
- **`X-Read-Source`:** Фізичне джерело отримання даних. Можливі значення:
  - `projection-store` — основне оптимізоване денормалізоване сховище (Elasticsearch, PostgreSQL Read View, Redis).
  - `primary-write-store` — транзакційне джерело правди (використано в режимі аварійного обходу або при рівні узгодженості `STRONG`).
  - `cache` — проміжний шар кешування перед моделлю читання.
  *Приклад:* `X-Read-Source: projection-store`
- **`X-Data-Freshness`:** Класифікація свіжості повернутого стану:
  - `FRESH` — стан повністю задовольняє вимогам контракту без додаткових затримок.
  - `AWAITED` — стан став свіжим у результаті успішного очікування наздоганяння проєкції.
  - `STALE` — повернуто застарілий стан, оскільки клієнт передав `X-Allow-Degraded: true`.
  *Приклад:* `X-Data-Freshness: AWAITED`
- **`X-Cross-Region-Lag-Ms`:** Додаткова затримка міжрегіональної реплікації у разі георозподіленого розгортання.
  *Приклад:* `X-Cross-Region-Lag-Ms: 65`

## 4. Специфікація кодів стану та діагностичних повідомлень (RFC 9457)

Якщо шлюз запитів не може виконати запит у межах узгодженого контракту, він відхиляє запит із поверненням документа `Problem Details`:

### Код `412 Precondition Failed` — порушення контракту свіжості
Повертається, коли поточний лаг моделі читання перевищує `X-Max-Staleness-Ms`, або версія `X-Required-Version` ще не досягнута проєктором, а клієнт заборонив деградацію (`X-Allow-Degraded: false`) та обхід первинної бази.

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/problem+json
X-Read-Model-Version: 88410
X-Read-Model-Lag-Ms: 680
Retry-After: 1

{
  "type": "https://api.example.com/problems/read-model-lag-exceeded",
  "title": "Порушення контракту свіжості моделі читання",
  "status": 412,
  "detail": "Поточний лаг проєкції 680 мс перевищує максимально допустимий ліміт 200 мс",
  "instance": "/orders/ORD-9142",
  "required_version": 88412,
  "current_version": 88410,
  "current_lag_ms": 680,
  "max_allowed_lag_ms": 200,
  "retry_after_ms": 150
}
```

### Код `504 Gateway Timeout` — вичерпано бюджет очікування наздоганяння
Повертається, коли шлюз читання заблокував запит на виконання очікування (`Wait-for-Version`), але за час `X-Max-Wait-Ms` проєктор не зміг застосувати потрібну версію через чергу в брокері повідомлень або блокування в базі даних.

```http
HTTP/1.1 504 Gateway Timeout
Content-Type: application/problem+json
X-Read-Model-Version: 88411
X-Read-Model-Lag-Ms: 320

{
  "type": "https://api.example.com/problems/projection-await-timeout",
  "title": "Вичерпано ліміт часу очікування версії",
  "status": 504,
  "detail": "Проєктор не досяг версії 88412 за виділений бюджет очікування 100 мс",
  "required_version": 88412,
  "last_processed_version": 88411,
  "waited_ms": 100,
  "recommended_fallback": "primary-write-store"
}
```

### Код `428 Precondition Required` — відсутній обов'язковий версійний токен
Повертається захищеними кінцевими точками читання, які за бізнес-правилами вимагають обов'язкового надання причинного токена (наприклад, сторінка підтвердження оплати після перенаправлення з платіжного шлюзу).

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/causal-token-required",
  "title": "Необхідно надати версійний токен",
  "status": 428,
  "detail": "Кінцева точка вимагає заголовок X-Required-Version або X-Session-Watermark для запобігання аномаліям читання"
}
```

## 5. gRPC та Protocol Buffers контракт

Для високопродуктивної міжсервісної взаємодії визначено наступні структури Protocol Buffers (v3):

```protobuf
syntax = "proto3";

package distributed.readmodel.v1;

// Рівень узгодженості запиту на читання
enum ConsistencyLevel {
  CONSISTENCY_LEVEL_UNSPECIFIED = 0;
  CONSISTENCY_LEVEL_EVENTUAL = 1;
  CONSISTENCY_LEVEL_BOUNDED_STALENESS = 2;
  CONSISTENCY_LEVEL_READ_YOUR_WRITES = 3;
  CONSISTENCY_LEVEL_MONOTONIC_READ = 4;
  CONSISTENCY_LEVEL_STRONG = 5;
}

// Параметри контракту, що передаються клієнтом
message ConsistencyContractOptions {
  ConsistencyLevel consistency_level = 1;
  uint64 required_version = 2;
  uint32 max_staleness_ms = 3;
  uint32 max_wait_ms = 4;
  bool allow_degraded = 5;
  uint64 session_watermark = 6;
}

// Метадані свіжості, що повертаються у відповіді
message ResponseFreshnessMetadata {
  uint64 read_model_version = 1;
  uint32 measured_lag_ms = 2;
  string read_source = 3;
  bool was_awaited = 4;
  bool is_degraded = 5;
  uint32 cross_region_lag_ms = 6;
}

// Запит на отримання агрегованого замовлення
message GetOrderQueryRequest {
  string order_id = 1;
  ConsistencyContractOptions consistency = 2;
}

// Відповідь із денормалізованими даними та метаданими свіжості
message GetOrderQueryResponse {
  string order_id = 1;
  string customer_id = 2;
  string status = 3;
  int64 total_cents = 4;
  repeated string item_ids = 5;
  ResponseFreshnessMetadata freshness = 6;
}

// Службовий сервіс моніторингу та керування ватерлініями проєкцій
service ReadModelLagService {
  rpc GetOrder(GetOrderQueryRequest) returns (GetOrderQueryResponse);
  rpc StreamWatermarks(WatermarkSubscriptionRequest) returns (stream WatermarkUpdate);
}

message WatermarkSubscriptionRequest {
  string projection_name = 1;
}

message WatermarkUpdate {
  string projection_name = 1;
  uint32 partition_id = 2;
  uint64 committed_offset = 3;
  uint32 physical_lag_ms = 4;
  int64 timestamp_mono = 5;
}
```

## 6. Приклади наскрізних сценаріїв взаємодії (HTTP Traces)

### Сценарій А: Успішне читання власних записів з очікуванням (Read-Your-Own-Writes)

Крок 1. Клієнт створює нову сутність через команду:
```http
POST /api/v1/orders HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"customer_id": "CUST-100", "total_cents": 45000}
```

Відповідь командного сервера:
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Causal-Token: 99420
X-Commit-Timestamp: 2026-08-20T14:40:00.010Z

{"order_id": "ORD-5512", "status": "PENDING"}
```

Крок 2. Клієнтський фронтенд негайно звертається до моделі читання, передаючи отриманий токен:
```http
GET /api/v1/orders/ORD-5512 HTTP/1.1
Host: api.example.com
X-Consistency-Level: READ_YOUR_WRITES
X-Required-Version: 99420
X-Max-Wait-Ms: 50
```

Відповідь шлюзу читання (проєктор наздогнав версію за 18 мс):
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Read-Model-Version: 99420
X-Read-Model-Lag-Ms: 18
X-Read-Source: projection-store
X-Data-Freshness: AWAITED

{
  "order_id": "ORD-5512",
  "customer_id": "CUST-100",
  "status": "PENDING",
  "total_cents": 45000,
  "created_at": "2026-08-20T14:40:00.010Z"
}
```

### Сценарій Б: Аварійний обхід первинного сховища у разі відставання проєкції

Клієнт вимагає версію `99420`, але проєктор перевантажений пакетною індексацією й не встигає за 50 мс:

```http
GET /api/v1/orders/ORD-5512 HTTP/1.1
Host: api.example.com
X-Consistency-Level: READ_YOUR_WRITES
X-Required-Version: 99420
X-Max-Wait-Ms: 50
```

Відповідь шлюзу читання (автоматичне перемикання на первинну реляційну базу):
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Read-Model-Version: 99420
X-Read-Source: primary-write-store
X-Data-Freshness: FRESH
X-Warning: 199 - "Projection lag exceeded threshold, served from primary"

{
  "order_id": "ORD-5512",
  "customer_id": "CUST-100",
  "status": "PENDING",
  "total_cents": 45000
}
```

## 7. Рекомендації щодо реалізації клієнтського SDK

Щоб прикладні розробники не писали низькорівневий код керування заголовками вручну, клієнтські бібліотеки (SDK) реалізують патерн автоматичного прокидання токенів (Automatic Causal Context Propagation):

1. **Перехоплювач відповідей (Response Interceptor):** перехоплює всі успішні відповіді від командних мутацій (`POST`, `PUT`, `PATCH`, `DELETE`), зчитує заголовок `X-Causal-Token` і зберігає його в пам'яті сесії (`sessionStorage` у браузері або `ThreadLocal` / `AsyncLocalStorage` на бекенді).
2. **Перехоплювач запитів (Request Interceptor):** перед виконанням будь-якого `GET`-запиту автоматично додає збережений токен у заголовок `X-Required-Version` та виставляє рівень `X-Consistency-Level: READ_YOUR_WRITES`.
3. **Обробка помилки 412 (Backoff and Retry):** якщо сервер повернув `412 Precondition Failed` із заголовком `Retry-After: 1`, SDK автоматично виконує повторний запит через зазначений інтервал без викидання винятку в бізнес-код користувача.
4. **Скидання токена за часом (Token TTL):** якщо з моменту останнього запису минуло більше часу, ніж максимальний гарантований лаг системи (наприклад, більше 5 секунд), токен видаляється з пам'яті, і наступні запити автоматично повертаються до дешевого режиму `EVENTUAL`.

Дотримання цієї специфікації повністю усуває стан гонитви між потоками запису та читання, забезпечуючи математично гарантовану поведінку розподіленого застосунку.
