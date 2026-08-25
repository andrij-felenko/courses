# 📋 Контракти, інтерфейси та схеми захисту від перегравання

Уніфікація протоколів захисту від перегравання в розподілених системах вимагає узгоджених контрактів на чотирьох взаємопов'язаних рівнях архітектури: мережеві HTTP/gRPC-заголовки, структури пам'яті фільтрів, DDL-схеми транзакційних сховищ та інтерфейси проміжного програмного забезпечення (middleware).

Без чіткого контракту розподілені компоненти неминуче розходяться у трактуванні часових зон, форматів серіалізації, правил сортування полів під час хешування або семантики кодів помилок, що відкриває приховані дірки для дублювання транзакцій.

## Протокольні заголовки HTTP та метадані gRPC

Для захисту відкритих API від перехоплення та системних повторів клієнт зобов'язаний супроводжувати кожен запит, що змінює стан (`POST`, `PUT`, `PATCH`, `DELETE`), набором стандартизованих заголовків.

| Заголовок / Метадані | Тип / Формат | Обов'язковість | Опис та семантика |
|---|---|---|---|
| `Idempotency-Key` | `UUIDv7` або `String(64)` | Обов'язковий для мутацій | Унікальний ідентифікатор бізнес-наміру клієнта. Забезпечує детерміновану відповідь при повторних викликах. |
| `X-Signature-Timestamp` | `Unix Epoch Milliseconds` | Обов'язковий при підписі | Час створення запиту на пристрої відправника. Використовується для валідації часового вікна `Δ_t`. |
| `X-Signature-Nonce` | `Hex(32)` (128 бітів) | Обов'язковий для HMAC | Одноразовий криптографічний токен, згенерований CSPRNG відправника. |
| `X-Signature` | `Hex(64)` (SHA-256 HMAC) | Обов'язковий для безпеки | Цифровий підпис канонічного рядка запиту: `HMAC_SHA256(Secret, CanonicalString)`. |
| `X-Fencing-Token` | `uint64` (монотонний) | Обов'язковий для воркерів | Номер епохи або монотонний токен блокування для захисту від зомбі-лідерів. |

### Формування канонічного рядка підпису та правила нормалізації

Криптографічний підпис `X-Signature` обчислюється над канонічним представленням запиту. Будь-яка розбіжність у пробілах, регістрі літер у заголовках або порядку параметрів URL призведе до хибного відхилення легітимного запиту.

Канонізація виконується за такими суворими правилами:
1. Метод HTTP наводиться у верхньому регістрі (наприклад, `POST`).
2. Шлях URI нормалізується: видаляються подвійні слеші, відносні сегменти (`/../`) та кінцевий слеш.
3. Часова мітка передається у вигляді цілого числа мілісекунд від початку епохи Unix (UTC).
4. Випадковий токен `Nonce` передається у нижньому регістрі у шістнадцятковому вигляді.
5. Тіло запиту гешується за алгоритмом SHA-256 у сирому бінарному вигляді до будь-яких трансформацій стиснення.

Структура канонічного рядка для розрахунку HMAC:

```
CanonicalString = 
    HTTP_METHOD + "\n" +
    CANONICAL_URI + "\n" +
    X_SIGNATURE_TIMESTAMP + "\n" +
    X_SIGNATURE_NONCE + "\n" +
    IDEMPOTENCY_KEY + "\n" +
    HEX_LOWERCASE(SHA256(REQUEST_BODY))
```

### Коди помилок та протокольні відповіді

Якщо запит порушує контракт свіжості або виявляється переграним дублікатом, сервер повертає стандартизовану HTTP/gRPC відповідь без виконання бізнес-логіки:

| Код HTTP | Код gRPC | Символічний статус | Причина відхилення запиту |
|---|---|---|---|
| `400 Bad Request` | `INVALID_ARGUMENT` | `ERR_MALFORMED_NONCE` | Формат Nonce, Timestamp або Idempotency-Key не відповідає стандарту (наприклад, пошкоджений UUID). |
| `401 Unauthorized` | `UNAUTHENTICATED` | `ERR_INVALID_SIGNATURE` | Криптографічний підпис не зійшовся з розрахованим HMAC. |
| `409 Conflict` | `ABORTED` | `ERR_DUPLICATE_IN_FLIGHT` | Запит із таким `Idempotency-Key` вже виконується прямо зараз іншим потоком. |
| `409 Conflict` | `FAILED_PRECONDITION` | `ERR_STALE_FENCING_TOKEN` | Номер епохи воркера менший або рівний максимальному номеру, зафіксованому в сховищі. |
| `422 Unprocessable` | `OUT_OF_RANGE` | `ERR_TIMESTAMP_EXPIRED` | Часова мітка `X-Signature-Timestamp` випала за межі допустимого вікна валідності (`|t_server - t_client| > Δ_t`). |
| `429 Too Many` | `RESOURCE_EXHAUSTED` | `ERR_REPLAY_FLOOD` | Виявлено серійне перегравання одного й того самого Nonce; спрацював rate-limiter. |

## Схеми реляційних та Key-Value сховищ

Нижче наведено промислові структури таблиць бази даних PostgreSQL та моделі ключів Redis для реалізації дворівневої системи відсікання дублікатів.

### PostgreSQL DDL: Секціонована таблиця Transactional Inbox

Секціонування за діапазоном дат (`Range Partitioning`) є критично важливим для забезпечення сталої швидкості роботи індексів. Без секціонування таблиця вхідних повідомлень через кілька місяців розростається до сотень мільйонів рядків. Видалення застарілих даних командою `DELETE` викликає блокування рядків, фрагментацію табличного простору (Table Bloat) та деградацію продуктивності автовакууму (PostgreSQL Autovacuum). Секціонування дозволяє очищати дані за минулі дні миттєвою операцією від'єднання та видалення секції `DROP TABLE`.

```sql
-- Перелік статусів життєвого циклу обробки повідомлення
CREATE TYPE inbox_status AS ENUM ('PROCESSING', 'PROCESSED', 'FAILED');

-- Головна таблиця вхідних повідомлень із Range-секціонуванням за датою створення
CREATE TABLE inbox_messages (
    idempotency_key   VARCHAR(64)  NOT NULL,
    consumer_group    VARCHAR(64)  NOT NULL,
    source_event_id   VARCHAR(64)  NOT NULL,
    fencing_token     BIGINT       NOT NULL DEFAULT 0,
    status            inbox_status NOT NULL DEFAULT 'PROCESSING',
    response_payload  JSONB        NULL,
    response_status   INT          NULL,
    error_message     TEXT         NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (created_at, consumer_group, idempotency_key)
) PARTITION BY RANGE (created_at);

-- Добові секції (приклад автоматичного або ручного створення)
CREATE TABLE inbox_messages_2026_08_20 PARTITION OF inbox_messages
    FOR VALUES FROM ('2026-08-20 00:00:00+00') TO ('2026-08-21 00:00:00+00');

CREATE TABLE inbox_messages_2026_08_21 PARTITION OF inbox_messages
    FOR VALUES FROM ('2026-08-21 00:00:00+00') TO ('2026-08-22 00:00:00+00');

-- Індекс для миттєвої перевірки дублікатів у межах групи споживачів
CREATE INDEX idx_inbox_consumer_lookup 
    ON inbox_messages (consumer_group, idempotency_key);
```

### PostgreSQL DDL: Бар'єр токенів огорожі (Fencing Tokens)

Ця таблиця забезпечує захист спільних ресурсів від зомбі-лідерів, які втратили право керування через мережевий спліт-брейн або тривалу паузу збирача сміття, але намагаються надіслати запізнілу мутацію.

Збережена процедура `verify_and_update_fencing` виконує атомарну перевірку номера токена в режимі блокування рядка `FOR UPDATE`. Якщо новий токен суворо більший за поточний максимум, оренда продовжується, а максимальний номер оновлюється. Якщо токен менший або дорівнює зафіксованому, процедура негайно повертає `FALSE`, що слугує сигналом для відхилення команди.

```sql
CREATE TABLE distributed_fencing_leases (
    resource_id       VARCHAR(128) PRIMARY KEY,
    owner_node_id     VARCHAR(64)  NOT NULL,
    max_fencing_token BIGINT       NOT NULL,
    lease_expires_at  TIMESTAMPTZ  NOT NULL,
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Атомарна перевірка та фіксація токена огорожі
CREATE OR REPLACE FUNCTION verify_and_update_fencing(
    p_resource_id   VARCHAR(128),
    p_node_id       VARCHAR(64),
    p_fencing_token BIGINT,
    p_lease_ttl_ms  INT
) RETURNS BOOLEAN AS $$
DECLARE
    v_current_token BIGINT;
BEGIN
    SELECT max_fencing_token INTO v_current_token
    FROM distributed_fencing_leases
    WHERE resource_id = p_resource_id
    FOR UPDATE;

    IF NOT FOUND THEN
        INSERT INTO distributed_fencing_leases(resource_id, owner_node_id, max_fencing_token, lease_expires_at)
        VALUES (p_resource_id, p_node_id, p_fencing_token, NOW() + (p_lease_ttl_ms || ' milliseconds')::INTERVAL);
        RETURN TRUE;
    END IF;

    IF p_fencing_token > v_current_token THEN
        UPDATE distributed_fencing_leases
        SET owner_node_id = p_node_id,
            max_fencing_token = p_fencing_token,
            lease_expires_at = NOW() + (p_lease_ttl_ms || ' milliseconds')::INTERVAL,
            updated_at = NOW()
        WHERE resource_id = p_resource_id;
        RETURN TRUE;
    ELSE
        -- Запізнілий запит зомбі-воркера відхиляється
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### Схема Redis для L1-кешу Nonce та ключів ідемпотентності

Використання Redis як прикордонного фільтра L1 дозволяє відсікати понад 99% повторних запитів до того, як вони навантажать транзакційне ядро реляційної бази даних.

* **Ключ Nonce (`replay:nonce:{tenant_id}:{nonce_hex}`):**
  Зберігає мітку часу першого отримання випадкового числа. Встановлюється атомарною командою `SET key value EX 300 NX`. Якщо команда повертає `nil`, це свідчить про спробу повторного надсилання того самого токена в межах 5-хвилинного вікна валідності.

* **Ключ блокування виконання In-Flight (`idemp:lock:{scope}:{idempotency_key}`):**
  Використовується для запобігання стану перегонів (Race Condition), коли клієнт паралельно надсилає кілька однакових запитів з одним ключем ідемпотентності. Встановлюється з коротким TTL (наприклад, 30 секунд), що відповідає максимальному таймауту обробки запиту сервером.

* **Ключ кешу збереженої відповіді (`idemp:resp:{scope}:{idempotency_key}`):**
  Містить повне серіалізоване тіло первинної відповіді, HTTP-статус та заголовки. При отриманні повторного запиту після успішного завершення операції шлюз негайно віддає кешовану відповідь, не передаючи запит у доменні сервіси.

## Інтерфейси обробників та перехоплювачів (Middleware)

Для безшовної інтеграції захисту від перегравання в конвеєр обробки запитів використовується патерн «Перехоплювач» (Interceptor). Перехоплювач ділить обробку на три фази:

1. **Фаза попередньої валідації (`pre_handle`):** перевіряє свіжість часової мітки, наявність Nonce у кеші та статус ключа ідемпотентності. Якщо запит уже виконано, повертає збережену відповідь; якщо виконується прямо зараз — повертає статус конфлікту `409 Conflict`.
2. **Фаза фіксації результату (`post_handle_success`):** зберігає сформовану відповідь у кеші та оновлює статус у базі даних на `PROCESSED`.
3. **Фаза обробки помилок (`post_handle_failure`):** у разі виникнення внутрішнього збою сервісу знімає блокування виконання, дозволяючи клієнту виконати повторну спробу (Retry).

Нижче наведено сигнатури інтерфейсів мовами C++ та C.

:::tabs
```cpp
#include <cstdint>
#include <string>
#include <string_view>
#include <memory>
#include <optional>
#include <chrono>

struct RequestContext {
    std::string_view idempotency_key;
    std::string_view nonce;
    std::string_view signature;
    std::chrono::system_clock::time_point timestamp;
    uint64_t fencing_token{0};
    std::string_view request_body;
};

enum class ValidationDecision {
    AllowFirstTime,
    ServeCachedResponse,
    RejectDuplicateInFlight,
    RejectExpiredTimestamp,
    RejectInvalidSignature,
    RejectStaleFencingToken
};

struct InterceptorResult {
    ValidationDecision decision;
    std::optional<std::string> cached_payload;
    int http_status_code{200};
    std::string error_message;
};

class IReplayProtectionInterceptor {
public:
    virtual ~IReplayProtectionInterceptor() = default;

    // Попередня перевірка до виклику доменної логіки
    [[nodiscard]] virtual InterceptorResult pre_handle(const RequestContext& ctx) = 0;

    // Фіксація успішного результату для ідемпотентних повторів
    virtual void post_handle_success(
        std::string_view idempotency_key,
        int status_code,
        std::string_view response_body
    ) = 0;

    // Скасування блокування при внутрішній системній помилці
    virtual void post_handle_failure(std::string_view idempotency_key) = 0;
};
```
```c
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <stddef.h>

typedef enum {
    DECISION_ALLOW_FIRST_TIME,
    DECISION_SERVE_CACHED_RESPONSE,
    DECISION_REJECT_DUPLICATE_IN_FLIGHT,
    DECISION_REJECT_EXPIRED_TIMESTAMP,
    DECISION_REJECT_INVALID_SIGNATURE,
    DECISION_REJECT_STALE_FENCING_TOKEN
} validation_decision_t;

typedef struct {
    const char* idempotency_key;
    const char* nonce;
    const char* signature;
    int64_t timestamp_ms;
    uint64_t fencing_token;
    const char* body;
    size_t body_len;
} request_context_t;

typedef struct {
    validation_decision_t decision;
    int http_status_code;
    const char* cached_payload;
    size_t cached_payload_len;
    char error_message[128];
} interceptor_result_t;

typedef struct replay_interceptor_vtable {
    interceptor_result_t (*pre_handle)(void* ctx, const request_context_t* req);
    void (*post_handle_success)(void* ctx, const char* idemp_key, int status, const char* resp, size_t resp_len);
    void (*post_handle_failure)(void* ctx, const char* idemp_key);
} replay_interceptor_vtable_t;

typedef struct {
    const replay_interceptor_vtable_t* vtable;
    void* impl_context;
} replay_interceptor_t;
```
:::

## Крайові сценарії та самовідновлення при аваріях

Під час промислової експлуатації перехоплювачів виникають специфічні збої, які вимагають заздалегідь визначених сценаріїв поведінки:

1. **Аварійне падіння вузла під час обробки:**
   Якщо сервер обробив транзакцію в базі даних, але аварійно впав до запису кешу в Redis або до відправки HTTP-відповіді клієнту, наступний запит клієнта з тим самим `Idempotency-Key` отримує `nil` у Redis. У цьому випадку перехоплювач зобов'язаний звернутися до таблиці `inbox_messages` у PostgreSQL. Знайшовши статус `PROCESSED`, шлюз відновлює ключ у Redis, повертає збережений `response_payload` клієнту і не виконує повторної мутації.

2. **Розсинхронізація серверних годинників (NTP Alerting):**
   Якщо локальний годинник вузла починає дрейфувати відносно еталонного часу кластера більше ніж на 500 мілісекунд, інфраструктура генерує сповіщення `NtpClockSkewExceeded`. При зростанні дрейфу вузол автоматично виводиться з пулу балансування навантаження, оскільки він ризикує масово відхиляти легітимні клієнтські запити або приймати застарілі пакети.

## Таблиця параметрів конфігурації

Налаштування параметрів захисту від перегравання вимагає ретельного інженерного балансування між стійкістю до мережевих збоїв та накладними витратами обчислювальних ресурсів.

| Параметр конфігурації | Тип | За замовчуванням | Рекомендований діапазон | Опис та інженерні ризики |
|---|---|---|---|---|
| `anti_replay.window_size_bits` | `int` | `64` | `64` – `1024` | Розмір бітмап-вікна на транспортному рівні. Якщо розмір менший за джитер мережі — виникають помилкові відхилення легітимних перевпорядкованих пакетів. |
| `anti_replay.timestamp_tolerance_sec` | `int` | `150` | `30` – `300` | Півширина вікна валідності часових міток `Δ_t`. Замале значення призводить до відхилення запитів від клієнтів із природним дрейфом годинників; завелике — збільшує обсяг кешу. |
| `anti_replay.nonce_ttl_sec` | `int` | `300` | `60` – `600` | Час життя ключа Nonce у Redis (`2 · Δ_t`). Замале значення створює дірку для перегравання після витіснення ключа; завелике — спричиняє перевитрату оперативної пам'яті. |
| `anti_replay.idempotency_cache_ttl_sec`| `int` | `86400` | `3600` – `604800` | Час зберігання готової відповіді в кеші (1–7 діб). Дозволяє миттєво повертати збережений результат клієнту при повторних спробах без повторного навантаження бази даних. |
| `anti_replay.fencing_lease_ttl_ms` | `int` | `5000` | `1000` – `15000` | Інтервал оренди токена огорожі. Повинен перевищувати інтервал серцебиття (heartbeat), але бути меншим за критичний час реакції на аварійне падіння вузла. |
| `anti_replay.bloom_generations` | `int` | `3` | `3` – `5` | Кількість часових поколінь фільтра Блума для плавної ротації пам'яті L1-дедуплікації без створення пауз збирача сміття та стрибків затримки. |
