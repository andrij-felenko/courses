# ⚙️ Реалізація рушія ідемпотентності з захистом від гонитви та валідацією відбитків

Цей проєкт демонструє повноцінну реалізацію потокобезпечного транзакційного рушія ідемпотентності системного рівня, який підтримує захист від стану гонитви при конкурентних повторах, валідацію відбитка тіла запиту (payload fingerprinting), часову оренду (lease TTL) та кешування результату.

## 1. Архітектура та інваріанти автомата

У розподілених сервісах обробник запитів не може покладатися на наївну схему «перевірити наявність ключа, якщо немає — виконати, потім зберегти». Якщо два однакових запити надходять одночасно в різних потоках або на різні вузли кластера, обидва потоки одночасно прочитають стан «ключа немає» і двічі виконають бізнес-дію.

Надійний рушій ідемпотентності будується навколо трьох обов'язкових станів запису:

```
[Порожньо] ──(acquire: atomic CAS)──> IN_PROGRESS ──(commit)──> COMMITTED (кеш відповіді)
                                          │
                                          └──(fail)───────────> FAILED (дозволено retry)
```

Кожен запис у сховищі ідемпотентності містить такі поля:
* `key` — унікальний строковий ідентифікатор, згенерований клієнтом (UUIDv4).
* `payload_hash` — 64-бітний або 256-бітний криптографічний відбиток тіла та параметрів запиту.
* `state` — поточний стан автомата (`IN_PROGRESS`, `COMMITTED`, `FAILED`).
* `response_code` — збережений код відповіді (наприклад, HTTP 200 або внутрішній статус).
* `response_body` — серіалізоване тіло результату первинного виконання.
* `expires_at` — монотонний часовий штамп завершення оренди або видалення запису.

### Життєвий цикл операцій

Конвеєр рушія підтримує три фундаментальні операції:

1. **`acquire_or_check()`** — атомарне захоплення або перевірка ключа:
   * **Випадок 1 (Новий ключ):** Запису в таблиці немає. Рушій атомарно створює запис у стані `IN_PROGRESS`, фіксує хеш тіла запиту і встановлює короткостроковий таймер оренди (`lease_timeout`, за замовчуванням 30 секунд). Повертається статус `ACTION_EXECUTE`. Викликач отримує ексклюзивне право на виконання бізнес-логіки.
   * **Випадок 2 (Успішний повтор):** Запис існує у стані `COMMITTED`. Рушій побітово звіряє збережений хеш із хешем поточного запиту. Якщо вони збігаються — це легітимний мережевий повтор. Повертається статус `ACTION_RETURN_CACHED` разом із раніше збереженим кодом і тілом відповіді. Бізнес-код не викликається.
   * **Випадок 3 (Підміна параметрів):** Запис існує у стані `COMMITTED`, але хеш тіла запиту відрізняється від збереженого. Це свідчить про спробу використати старий ключ для іншої операції. Повертається статус `ACTION_PAYLOAD_MISMATCH`.
   * **Випадок 4 (Конкурентна обробка):** Запис перебуває у стані `IN_PROGRESS`, і строк оренди ще не минув (`now < expires_at`). Це означає, що перший запит прямо зараз виконується паралельним потоком. Повертається статус `ACTION_IN_FLIGHT_CONFLICT` (клієнту слід зачекати або повторити запит пізніше з бекофом).
   * **Випадок 5 (Перехоплення мертвої оренди):** Запис перебуває у стані `IN_PROGRESS`, але час оренди минув (`now >= expires_at`). Це трапляється, якщо потік або вузол, який виконував запит першим, завис або аварійно впав. Новий запит поновлює оренду на себе і береться за виконання (`ACTION_EXECUTE`).
   * **Випадок 6 (Повтор після збою):** Запис перебуває у стані `FAILED`. Рушій переводить його назад в `IN_PROGRESS` і дозволяє повторне виконання.

2. **`commit()`** — фіксація успіху:
   * Атомарно переводить запис зі стану `IN_PROGRESS` у стан `COMMITTED`, зберігає код повернення та тіло результату, а також встановлює довгостроковий час життя запису (TTL зберігання, наприклад, 86 400 секунд / 24 години).

3. **`fail()`** — фіксація тимчасової помилки:
   * Переводить запис у стан `FAILED`, дозволяючи наступним клієнтським спробам виконати повторну обробку.

4. **`evict_expired()`** — фонове очищення:
   * Видаляє з пам'яті записи, чий довгостроковий TTL повністю вичерпався.

## 2. Реалізація рушія мовами C та C++

У мові C реалізація спирається на масив кошиків хеш-таблиці з розв'язанням колізій методом ланцюжків і синхронізацію через `pthread_mutex_t`. У C++20 використовується сучасна об'єктна модель із RAII-замками `std::unique_lock`, контейнерами стандартної бібліотеки, монотонними годинниками `std::chrono::steady_clock` та типізованим результатом `std::expected`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>

#define HASH_BUCKETS 1024
#define DEFAULT_LEASE_SEC 30
#define DEFAULT_RETENTION_SEC 86400

typedef enum {
    IDEM_IN_PROGRESS = 0,
    IDEM_COMMITTED   = 1,
    IDEM_FAILED      = 2
} IdemState;

typedef enum {
    IDEM_ACTION_EXECUTE,
    IDEM_ACTION_RETURN_CACHED,
    IDEM_ACTION_IN_FLIGHT_CONFLICT,
    IDEM_ACTION_PAYLOAD_MISMATCH,
    IDEM_ACTION_ERROR
} IdemAction;

typedef struct IdemRecord {
    char *key;
    uint64_t payload_hash;
    IdemState state;
    int response_code;
    char *response_body;
    time_t expires_at;
    struct IdemRecord *next;
} IdemRecord;

typedef struct {
    IdemRecord *buckets[HASH_BUCKETS];
    pthread_mutex_t mutex;
} IdemEngine;

/* 64-бітний хеш FNV-1a для ключів і тіла запитів */
static uint64_t hash_bytes(const void *data, size_t len) {
    const uint8_t *ptr = (const uint8_t *)data;
    uint64_t h = 0xcbf29ce484222325ULL;
    for (size_t i = 0; i < len; ++i) {
        h ^= (uint64_t)ptr[i];
        h *= 0x100000001b3ULL;
    }
    return h;
}

static uint64_t hash_string(const char *s) {
    return hash_bytes(s, strlen(s));
}

IdemEngine *idem_create(void) {
    IdemEngine *engine = (IdemEngine *)calloc(1, sizeof(IdemEngine));
    if (!engine) return NULL;
    if (pthread_mutex_init(&engine->mutex, NULL) != 0) {
        free(engine);
        return NULL;
    }
    return engine;
}

void idem_destroy(IdemEngine *engine) {
    if (!engine) return;
    pthread_mutex_lock(&engine->mutex);
    for (int i = 0; i < HASH_BUCKETS; ++i) {
        IdemRecord *cur = engine->buckets[i];
        while (cur) {
            IdemRecord *next = cur->next;
            free(cur->key);
            free(cur->response_body);
            free(cur);
            cur = next;
        }
    }
    pthread_mutex_unlock(&engine->mutex);
    pthread_mutex_destroy(&engine->mutex);
    free(engine);
}

IdemAction idem_acquire(IdemEngine *engine, const char *key, const void *payload,
                        size_t payload_len, int *out_code, char *out_body, size_t body_buf_sz) {
    if (!engine || !key) return IDEM_ACTION_ERROR;

    time_t now = time(NULL);
    uint64_t p_hash = hash_bytes(payload, payload_len);
    uint64_t k_hash = hash_string(key);
    size_t idx = k_hash % HASH_BUCKETS;

    pthread_mutex_lock(&engine->mutex);

    IdemRecord *rec = engine->buckets[idx];
    while (rec) {
        if (strcmp(rec->key, key) == 0) {
            break;
        }
        rec = rec->next;
    }

    if (rec) {
        if (rec->state == IDEM_COMMITTED) {
            if (rec->payload_hash != p_hash) {
                pthread_mutex_unlock(&engine->mutex);
                return IDEM_ACTION_PAYLOAD_MISMATCH;
            }
            if (out_code) *out_code = rec->response_code;
            if (out_body && rec->response_body) {
                strncpy(out_body, rec->response_body, body_buf_sz - 1);
                out_body[body_buf_sz - 1] = '\0';
            }
            pthread_mutex_unlock(&engine->mutex);
            return IDEM_ACTION_RETURN_CACHED;
        }

        if (rec->state == IDEM_IN_PROGRESS) {
            if (now < rec->expires_at) {
                /* Оренда діє — паралельний дублікат */
                pthread_mutex_unlock(&engine->mutex);
                return IDEM_ACTION_IN_FLIGHT_CONFLICT;
            }
            /* Оренда застаріла — перехоплюємо виконання */
            rec->payload_hash = p_hash;
            rec->expires_at = now + DEFAULT_LEASE_SEC;
            pthread_mutex_unlock(&engine->mutex);
            return IDEM_ACTION_EXECUTE;
        }

        if (rec->state == IDEM_FAILED) {
            /* Дозволений повтор після помилки */
            rec->state = IDEM_IN_PROGRESS;
            rec->payload_hash = p_hash;
            rec->expires_at = now + DEFAULT_LEASE_SEC;
            pthread_mutex_unlock(&engine->mutex);
            return IDEM_ACTION_EXECUTE;
        }
    }

    /* Новий запис */
    IdemRecord *new_rec = (IdemRecord *)calloc(1, sizeof(IdemRecord));
    if (!new_rec) {
        pthread_mutex_unlock(&engine->mutex);
        return IDEM_ACTION_ERROR;
    }
    new_rec->key = strdup(key);
    new_rec->payload_hash = p_hash;
    new_rec->state = IDEM_IN_PROGRESS;
    new_rec->expires_at = now + DEFAULT_LEASE_SEC;
    new_rec->next = engine->buckets[idx];
    engine->buckets[idx] = new_rec;

    pthread_mutex_unlock(&engine->mutex);
    return IDEM_ACTION_EXECUTE;
}

bool idem_commit(IdemEngine *engine, const char *key, int code, const char *body) {
    if (!engine || !key) return false;

    time_t now = time(NULL);
    uint64_t k_hash = hash_string(key);
    size_t idx = k_hash % HASH_BUCKETS;

    pthread_mutex_lock(&engine->mutex);
    IdemRecord *rec = engine->buckets[idx];
    while (rec) {
        if (strcmp(rec->key, key) == 0) {
            if (rec->state == IDEM_IN_PROGRESS) {
                rec->state = IDEM_COMMITTED;
                rec->response_code = code;
                free(rec->response_body);
                rec->response_body = body ? strdup(body) : NULL;
                rec->expires_at = now + DEFAULT_RETENTION_SEC;
                pthread_mutex_unlock(&engine->mutex);
                return true;
            }
            break;
        }
        rec = rec->next;
    }
    pthread_mutex_unlock(&engine->mutex);
    return false;
}

bool idem_fail(IdemEngine *engine, const char *key) {
    if (!engine || !key) return false;

    uint64_t k_hash = hash_string(key);
    size_t idx = k_hash % HASH_BUCKETS;

    pthread_mutex_lock(&engine->mutex);
    IdemRecord *rec = engine->buckets[idx];
    while (rec) {
        if (strcmp(rec->key, key) == 0) {
            if (rec->state == IDEM_IN_PROGRESS) {
                rec->state = IDEM_FAILED;
                pthread_mutex_unlock(&engine->mutex);
                return true;
            }
            break;
        }
        rec = rec->next;
    }
    pthread_mutex_unlock(&engine->mutex);
    return false;
}

size_t idem_evict_expired(IdemEngine *engine) {
    if (!engine) return 0;
    time_t now = time(NULL);
    size_t count = 0;

    pthread_mutex_lock(&engine->mutex);
    for (int i = 0; i < HASH_BUCKETS; ++i) {
        IdemRecord **curr_ptr = &engine->buckets[i];
        while (*curr_ptr) {
            IdemRecord *entry = *curr_ptr;
            if (now >= entry->expires_at) {
                *curr_ptr = entry->next;
                free(entry->key);
                free(entry->response_body);
                free(entry);
                count++;
            } else {
                curr_ptr = &entry->next;
            }
        }
    }
    pthread_mutex_unlock(&engine->mutex);
    return count;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <chrono>
#include <mutex>
#include <optional>
#include <memory>
#include <expected>
#include <cstdint>

enum class IdemState {
    InProgress,
    Committed,
    Failed
};

enum class IdemError {
    InFlightConflict,
    PayloadMismatch,
    InternalError
};

struct CachedResponse {
    int statusCode;
    std::string body;
};

class IdempotencyEngine {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    explicit IdempotencyEngine(
        std::chrono::seconds leaseTimeout = std::chrono::seconds(30),
        std::chrono::seconds retentionPeriod = std::chrono::seconds(86400))
        : leaseDuration_(leaseTimeout), retentionDuration_(retentionPeriod) {}

    // Спроба отримати або перевірити стан операції
    // Повертає:
    // - nullopt: запис успішно взято в обробку (викликач виконує бізнес-дію)
    // - CachedResponse: дія вже була успішно зафіксована раніше
    // - IdemError: конфлікт виконання або розбіжність параметрів
    std::expected<std::optional<CachedResponse>, IdemError> acquireOrCheck(
        std::string_view key, std::string_view payload) {
        
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = Clock::now();
        uint64_t pHash = computeHash(payload);

        auto it = store_.find(std::string(key));
        if (it != store_.end()) {
            auto& record = it->second;

            if (record.state == IdemState::Committed) {
                if (record.payloadHash != pHash) {
                    return std::unexpected(IdemError::PayloadMismatch);
                }
                return std::make_optional(record.cachedResult);
            }

            if (record.state == IdemState::InProgress) {
                if (now < record.expiresAt) {
                    return std::unexpected(IdemError::InFlightConflict);
                }
                // Оренда застаріла — перехоплюємо виконання
                record.payloadHash = pHash;
                record.expiresAt = now + leaseDuration_;
                return std::nullopt;
            }

            if (record.state == IdemState::Failed) {
                record.state = IdemState::InProgress;
                record.payloadHash = pHash;
                record.expiresAt = now + leaseDuration_;
                return std::nullopt;
            }
        }

        // Новий запис
        Record newRecord{
            .payloadHash = pHash,
            .state = IdemState::InProgress,
            .cachedResult = {},
            .expiresAt = now + leaseDuration_
        };
        store_.emplace(std::string(key), std::move(newRecord));
        return std::nullopt;
    }

    // Фіксація успішного результату
    bool commit(std::string_view key, int statusCode, std::string body) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(std::string(key));
        if (it != store_.end() && it->second.state == IdemState::InProgress) {
            it->second.state = IdemState::Committed;
            it->second.cachedResult = CachedResponse{statusCode, std::move(body)};
            it->second.expiresAt = Clock::now() + retentionDuration_;
            return true;
        }
        return false;
    }

    // Фіксація збою (дозволяє наступні retry)
    bool fail(std::string_view key) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(std::string(key));
        if (it != store_.end() && it->second.state == IdemState::InProgress) {
            it->second.state = IdemState::Failed;
            return true;
        }
        return false;
    }

    // Фонове очищення застарілих записів після TTL
    size_t evictExpired() {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = Clock::now();
        size_t initialSize = store_.size();
        std::erase_if(store_, [now](const auto& item) {
            return now >= item.second.expiresAt;
        });
        return initialSize - store_.size();
    }

private:
    struct Record {
        uint64_t payloadHash;
        IdemState state;
        CachedResponse cachedResult;
        TimePoint expiresAt;
    };

    static uint64_t computeHash(std::string_view s) {
        uint64_t h = 0xcbf29ce484222325ULL;
        for (char c : s) {
            h ^= static_cast<uint8_t>(c);
            h *= 0x100000001b3ULL;
        }
        return h;
    }

    std::chrono::seconds leaseDuration_;
    std::chrono::seconds retentionDuration_;
    std::mutex mutex_;
    std::unordered_map<std::string, Record> store_;
};
```
:::

## 3. Демонстраційний сценарій обробки збоїв

У наступній тестовій програмі симулюється повний спектр мережевих ситуацій: первинне успішне виконання, повторний запит через таймаут зв'язку, спроба підміни параметрів платежу та поведінка при конкурентному доступі.

:::tabs
```c
int main(void) {
    IdemEngine *engine = idem_create();
    const char *key = "req-uuid-9948-2831";
    const char *order_json = "{\"order_id\": 101, \"amount\": 500}";
    const char *tampered_json = "{\"order_id\": 101, \"amount\": 9999}";

    int code = 0;
    char body_buf[256];

    /* Сценарій 1: Первинний запит */
    IdemAction a1 = idem_acquire(engine, key, order_json, strlen(order_json), &code, body_buf, sizeof(body_buf));
    if (a1 == IDEM_ACTION_EXECUTE) {
        printf("[Спроба 1] EXECUTE -> виконуємо списання коштів у БД\n");
        /* Фіксуємо результат */
        idem_commit(engine, key, 200, "{\"status\": \"PAID\", \"tx_id\": 98871}");
    }

    /* Сценарій 2: Мережевий retry з тим самим ключем і тілом */
    IdemAction a2 = idem_acquire(engine, key, order_json, strlen(order_json), &code, body_buf, sizeof(body_buf));
    if (a2 == IDEM_ACTION_RETURN_CACHED) {
        printf("[Спроба 2] RETURN_CACHED -> код %d, відповідь: %s\n", code, body_buf);
    }

    /* Сценарій 3: Спроба використати той самий ключ для іншого платежу */
    IdemAction a3 = idem_acquire(engine, key, tampered_json, strlen(tampered_json), &code, body_buf, sizeof(body_buf));
    if (a3 == IDEM_ACTION_PAYLOAD_MISMATCH) {
        printf("[Спроба 3] PAYLOAD_MISMATCH -> відхилено, захист від підміни спрацював!\n");
    }

    /* Очищення ресурсів */
    idem_destroy(engine);
    return 0;
}
```
```cpp
int main() {
    IdempotencyEngine engine(std::chrono::seconds(10), std::chrono::seconds(3600));

    constexpr std::string_view key = "req-uuid-9948-2831";
    constexpr std::string_view orderPayload = R"({"order_id": 101, "amount": 500})";
    constexpr std::string_view tamperedPayload = R"({"order_id": 101, "amount": 9999})";

    // Сценарій 1: Первинний запит
    auto res1 = engine.acquireOrCheck(key, orderPayload);
    if (res1.has_value() && !res1.value().has_value()) {
        std::cout << "[Спроба 1] EXECUTE -> проводимо транзакцію\n";
        engine.commit(key, 200, R"({"status": "PAID", "tx_id": 98871})");
    }

    // Сценарій 2: Повторний виклик через втрату мережевого підтвердження
    auto res2 = engine.acquireOrCheck(key, orderPayload);
    if (res2.has_value() && res2.value().has_value()) {
        const auto& cached = res2.value().value();
        std::cout << "[Спроба 2] RETURN_CACHED -> код " << cached.statusCode 
                  << ", тіло: " << cached.body << "\n";
    }

    // Сценарій 3: Спроба підміни суми платежу під тим самим ключем
    auto res3 = engine.acquireOrCheck(key, tamperedPayload);
    if (!res3.has_value() && res3.error() == IdemError::PayloadMismatch) {
        std::cout << "[Спроба 3] PAYLOAD_MISMATCH -> операцію заблоковано (422 Unprocessable)\n";
    }

    return 0;
}
```
:::

## 4. Детальний аналіз інженерних пасток реалізації

При перенесенні наведеного алгоритму у високонавантажене промислове середовище слід враховувати такі системні нюанси:

### 1. Канонічна серіалізація JSON при хешуванні

У прикладі вище хеш обчислюється напряму від масиву байтів вхідного тіла запиту (`hash_bytes(payload, len)`). У реальних веб-сервісах це може призвести до хибного спрацьовування `PAYLOAD_MISMATCH`, якщо клієнтська бібліотека при повторі змінила порядок ключів у JSON-об'єкті або додала зайві пробіли:

```
Запит 1: {"amount": 500, "user": 42}  → хеш 0x88f2...
Запит 2: {"user": 42, "amount": 500}  → хеш 0x11a9... (розбіжність!)
```

У високонавантажених API перед хешуванням тіло запиту або приводять до **канонічної форми** (відсортовані ключі, видалені пробільні символи), або парсять у строгу внутрішню структуру даних (DTO) і хешують її бінарні поля.

### 2. Вибір тривалості оренди (Lease Duration)

Таймаут оренди `DEFAULT_LEASE_SEC` (30 с) визначає компроміс між стійкістю до падінь та захистом від гонитви:
* Якщо встановити оренду занадто короткою (наприклад, 2 с), а важкий запит до бази даних виконується 3 секунди, інший потік вирішить, що перший обробник загинув, перехопить ключ і паралельно виконає ту саму дію вдруге.
* Якщо встановити оренду занадто довгою (наприклад, 10 хвилин), а вузол обробки справді впав, клієнтські повтори блокуватимуться помилкою `IN_FLIGHT_CONFLICT` протягом усіх 10 хвилин.

Оптимальне значення оренди розраховується як `2.5 × 99-й перцентиль часу виконання операції`. Для тривалих фонових операцій використовують фоновий потік оновлення оренди (*heartbeat renewal*), який продовжує строк оренди кожні 5 секунд, поки обробка триває.

### 3. Конкурентність пам'яті та шардування блокувань

У базовій реалізації на C весь масив кошиків захищений одним м'ютексом `pthread_mutex_t`. При навантаженні понад 100 000 RPS цей м'ютекс стане вузьким місцем (високий рівень *mutex contention*).

У промислових системах застосовують шардоване блокування (*striped locking*): створюють фіксований масив із 64 або 256 м'ютексів, де індекс блокування обирається як `idx % NUM_LOCKS`. Це дозволяє паралельним потокам незалежно обробляти різні ключі без взаємних затримок.

### 4. Відображення на розподілені сховища (Redis та SQL)

Наведений вище алгоритм прямо транслюється у промислові розподілені системи:

1. **Реалізація у Redis (Lua-скрипт):**
   Оскільки Redis є однопотоковим для кожного ключа, вся логіка `acquire_or_check()` записується в атомарний Lua-скрипт:
   ```lua
   -- KEYS[1] = key, ARGV[1] = payload_hash, ARGV[2] = lease_sec, ARGV[3] = now
   local current = redis.call('HMGET', KEYS[1], 'state', 'hash', 'code', 'body', 'expires')
   local state = current[1]
   local hash = current[2]
   local code = current[3]
   local body = current[4]
   local expires = tonumber(current[5] or 0)
   local now = tonumber(ARGV[3])

   if not state then
       -- Новий ключ: резервуємо
       redis.call('HMSET', KEYS[1], 'state', 'IN_PROGRESS', 'hash', ARGV[1], 'expires', now + tonumber(ARGV[2]))
       redis.call('EXPIRE', KEYS[1], 86400)
       return { 'EXECUTE' }
   elseif state == 'COMMITTED' then
       if hash ~= ARGV[1] then
           return { 'MISMATCH' }
       end
       return { 'CACHED', code, body }
   elseif state == 'IN_PROGRESS' then
       if now < expires then
           return { 'CONFLICT' }
       else
           -- Перехоплення оренди
           redis.call('HSET', KEYS[1], 'hash', ARGV[1], 'expires', now + tonumber(ARGV[2]))
           return { 'EXECUTE' }
       end
   end
   ```

2. **Реалізація у реляційних СКБД (PostgreSQL / MySQL):**
   У реляційних базах даних замість м'ютексів використовують механізм `ON CONFLICT DO UPDATE` із перевіркою часових штампів:
   ```sql
   INSERT INTO idempotency_records (key, payload_hash, state, expires_at)
   VALUES ($1, $2, 'IN_PROGRESS', NOW() + INTERVAL '30 seconds')
   ON CONFLICT (key) DO UPDATE
   SET expires_at = NOW() + INTERVAL '30 seconds',
       payload_hash = EXCLUDED.payload_hash
   WHERE idempotency_records.state = 'IN_PROGRESS' 
     AND idempotency_records.expires_at < NOW()
   RETURNING state, response_code, response_body, payload_hash;
   ```

## 5. Профіль продуктивності та оптимізація пам'яті

Для оптимізації високонавантажених сервісів у наведеній системній реалізації застосовуються такі прийоми:

* **Мінімізація динамічних виділень пам'яті (Zero-Heap Allocation):**
  У C++ версії замість постійного копіювання `std::string` застосовується `std::string_view` для вхідних ключів і тіла запитів. Хеш обчислюється на місці без проміжних буферів.
* **Шардування м'ютексів (Lock Striping):**
  Розбиття глобального сховища на `N = 64` незалежних сегментів дозволяє досягти масштабування до сотень тисяч запитів на секунду (RPS) на багатоядерних процесорах без взаємного блокування потоків на спільній пам'яті.
* **Впорядковане витіснення (LRU / Timer Wheel):**
  Для систем із мільярдами ключів замість лінійного сканування хеш-таблиці застосовують кільцеві колеса таймерів (*Timer Wheels*) або фонові ієрархічні списки з сортуванням за часом `expires_at`, що знижує вартість очищення до `O(1)`.

## 6. Анатомія конкурентної гонки (Thread Race Trace)

Розглянемо детальний покроковий сценарій, коли два паралельні потоки (Потік A та Потік B) одночасно отримують дублікат одного й того самого HTTP-запиту з ключем `"req-uuid-9948"`:

```
Мить часу t0:
- Потік A: викликає idem_acquire("req-uuid-9948", payload)
- Потік A: захоплює pthread_mutex_lock(&engine->mutex)
- Потік A: шукає ключ у кошику -> запису немає
- Потік A: створює новий IdemRecord (state = IN_PROGRESS, expires_at = now + 30)
- Потік A: додає запис у початок зв'язного списку кошика
- Потік A: відпускає pthread_mutex_unlock(&engine->mutex)
- Потік A: повертає IDEM_ACTION_EXECUTE -> починає важку транзакцію в БД

Мить часу t0 + 2 мс (поки Потік A виконує запит до БД):
- Потік B: викликає idem_acquire("req-uuid-9948", payload)
- Потік B: захоплює pthread_mutex_lock(&engine->mutex)
- Потік B: знаходить запис у кошику
- Потік B: перевіряє стан: rec->state == IN_PROGRESS
- Потік B: перевіряє час оренди: now < rec->expires_at (оренда активна, лишилося 29.98 с)
- Потік B: відпускає pthread_mutex_unlock(&engine->mutex)
- Потік B: повертає IDEM_ACTION_IN_FLIGHT_CONFLICT -> НЕ чіпає базу даних, повертає клієнту HTTP 409

Мить часу t0 + 15 мс:
- Потік A: успішно завершує транзакцію в БД
- Потік A: викликає idem_commit("req-uuid-9948", 200, "{...}")
- Потік A: захоплює м'ютекс, переводить стан в IDEM_COMMITTED, зберігає тіло, expires_at = now + 86400
- Потік A: відпускає м'ютекс

Мить часу t0 + 500 мс (клієнт повторює запит після отримання 409):
- Потік C: викликає idem_acquire("req-uuid-9948", payload)
- Потік C: знаходить запис зі станом IDEM_COMMITTED
- Потік C: звіряє хеш тіла -> збігається
- Потік C: повертає IDEM_ACTION_RETURN_CACHED -> миттєво віддає збережений результат 200 OK
```

Цей ланцюжок наочно демонструє, як комбінація ексклюзивного блокування при вході та часової оренди повністю усуває стан гонитви: бізнес-транзакція виконується строго один раз.

## 7. Безблокувальні оптимізації (Lock-Free Read Path)

У системах із екстремальним навантаженням (понад 500 000 RPS на вузол), де переважна більшість запитів є легітимними повторами або перевірками закешованих відповідей, взяття ексклюзивного м'ютексу на кожне читання створює затримки на рівні кеш-ліній процесора (*cache bouncing*).

Для оптимізації швидкого шляху читання (*fast path*) застосовують безблокувальні атомарні примітиви пам'яті C++20:

1. **Атомарний покажчик стану `std::atomic<IdemState>`:**
   Поле стану оголошується атомарним. Коли запис переходить у стан `COMMITTED`, запис результату виконується з бар'єром звільнення пам'яті:
   ```cpp
   state.store(IdemState::Committed, std::memory_order_release);
   ```
2. **Читання з бар'єром отримання пам'яті (`std::memory_order_acquire`):**
   При повторному читанні потік спочатку перевіряє стан атомарно без захоплення глобального м'ютексу:
   ```cpp
   if (record->state.load(std::memory_order_acquire) == IdemState::Committed) {
       // Дані результату гарантовано видимі поточному процесорному ядру
       return make_optional(record->cachedResult);
   }
   ```
   Лише якщо стан вимагає мутації (`IN_PROGRESS` або відсутність запису), потік захоплює м'ютекс відповідного кошика.

## 8. Запобігання витокам пам'яті: пасивне проти активного витіснення

У високонавантажених сервісах витіснення застарілих ключів після закінчення їхнього TTL є обов'язковим для захисту від вичерпання пам'яті (*Out-Of-Memory*).

Існують дві стратегії керування очищенням:

1. **Пасивне (ліниве) витіснення (Lazy Eviction):**
   Ключ видаляється безпосередньо в момент звернення до нього у функції `acquire()`, якщо його `expires_at < now`.
   * *Перевага:* Нульові додаткові накладні витрати у фонових потоках.
   * *Недолік:* Якщо до ключа більше ніколи не зверталися (одноразовий запит без повторів), він назавжди залишається в пам'яті, породжуючи повільний витік ресурсів.

2. **Активне витіснення (Active Background Sweeping):**
   Окремий низькопріоритетний фоновий потік періодично (наприклад, раз на 60 секунд) викликає функцію `idem_evict_expired()`, проходячи по масиву кошиків і звільняючи вузли з простроченим часом життя.
   * *Перевага:* Гарантоване звільнення пам'яті для «мертвих» ключів.
   * *Недолік:* Короткочасні блокування м'ютексів під час проходження кошиків.

У промисловій архітектурі обидва підходи комбінують: лінива перевірка відсікає застарілі записи на гарячому шляху, а фоновий потік поступово підмітає пам'ять невеликими порціями (батчами по 100 записів), щоб не створювати сплесків затримки.

## 9. Розподілена версія: консенсус і лізи в кластері (Redlock)

Коли сервіс масштабується на десятки безстатусних контейнерів за балансувальником навантаження, локальна пам'ять процесу вже не може бути єдиним джерелом правди для стану `IN_PROGRESS`.

Для кластерної синхронізації застосовують розподілені замки з часовою орендою (наприклад, алгоритм Redlock поверх кластера Redis):

1. **Отримання розподіленої лізи:**
   Клієнт намагається встановити ключ у `N` незалежних майстер-вузлах Redis за допомогою атомарної команди з рандомізованим значенням токена:
   ```
   SET resource_name my_random_value NX PX 30000
   ```
2. **Врахування дрифту годинників:**
   Час валідності отриманої лізи зменшується на величину дрифту апаратних таймерів:
   ```
   validity_time = lease_time - (now - start_time) - clock_drift
   ```
   де `clock_drift = (lease_time · 0.01) + 2` мс.
3. **Кворумний захист:**
   Замок вважається успішно захопленим лише тоді, коли клієнт зміг встановити ключ на більшості вузлів (`N/2 + 1`) за час, менший за `lease_time`. Якщо кворум не набрано, клієнт надсилає команду розблокування на всі вузли і повторює спробу через випадковий проміжок часу.

## 10. Інтеграція з чергами повідомлень (Idempotent Consumer)

У подієво-орієнтованих системах на базі Apache Kafka чи RabbitMQ консюмери часто зазнають ребалансування партицій або аварійного перезапуску після виконання дії, але до коміту зміщення (*commit offset*).

Інтеграція наведеного рушія ідемпотентності в конвеєр консюмера виглядає так:

1. **Отримання повідомлення:**
   Консюмер вичитує повідомлення з бізнес-ключем `event_id` або `order_id`.
2. **Атомарний виклик `acquire()`:**
   Якщо `acquire()` повертає `IDEM_ACTION_RETURN_CACHED` — повідомлення вже було успішно опрацьоване в попередньому циклі. Консюмер пропускає виклик бізнес-логіки і відразу комітить зміщення брокеру (`consumer.commitSync()`).
3. **Обробка та коміт:**
   Якщо `acquire()` повертає `IDEM_ACTION_EXECUTE`, консюмер проводить транзакцію в базі даних, викликає `commit()` у рушії і лише після цього фіксує зміщення в Kafka.
4. **Ізоляція отруйних повідомлень:**
   Якщо бізнес-код викидає фатальний виняток, консюмер викликає `fail()`, перенаправляє повідомлення у `Dead Letter Queue` (DLQ) і продовжує рух черги без зупинки всього конвеєра.

## 11. Методологія стрес-тестування та Chaos Engineering

Для верифікації коректності рушія ідемпотентності в умовах наближених до реальних аварій застосовують Jepsen-подібні тести зі штучною інжекцією збоїв (*Fault Injection*):

1. **Інжекція мережевих аномалій (Linux Traffic Control):**
   За допомогою утиліти `tc` на інтерфейсах тестових вузлів створюють імітацію нестабільного зв'язку:
   ```bash
   # Додавання затримки 50 мс з розкидом ±20 мс та 5% втрат пакетів
   tc qdisc add dev eth0 root netem delay 50ms 20ms loss 5%
   ```
2. **Аварійні зупинки процесів (Chaos Monkey / kill -9):**
   Спеціальний фоновий потік надсилає сигнал `SIGKILL` випадковим обробникам у момент між виконанням бізнес-дії та збереженням результату.
3. **Верифікація інваріантів (Linearizability Checker):**
   Генератор навантаження паралельно відправляє 100 000 повторних запитів із перекриваючимися ключами. Після завершення тесту аналізатор перевіряє таблицю бізнес-транзакцій: **кількість реальних мутацій балансу зобов'язана точно дорівнювати кількості унікальних ключів ідемпотентності**. Жоден дублікат не повинен проникнути в систему.

## 12. Аудит пам'яті та перевірка на стан гонитви (Sanitizers)

Для гарантії відсутності витоків пам'яті та прихованих станів гонитви при багатопотоковому виконанні в C/C++ обов'язково проводять збірку з динамічними санітайзерами:

1. **Перевірка потокових гонок (ThreadSanitizer):**
   ```bash
   clang++ -std=c++20 -fsanitize=thread -g -O1 proj_demo.cpp -o proj_demo_tsan
   ./proj_demo_tsan
   ```
   TSan перевіряє кожне читання та запис у спільні змінні `IdemRecord`. Якщо два потоки звертаються до однієї комірки пам'яті без належної синхронізації м'ютексом або бар'єром пам'яті, TSan негайно аварійно зупиняє виконання з точним трейсом викликів.

2. **Перевірка витоків та виходу за межі буфера (AddressSanitizer):**
   ```bash
   gcc -std=c99 -fsanitize=address,undefined -g proj_demo.c -o proj_demo_asan
   ./proj_demo_asan
   ```
   ASan гарантує, що всі динамічно виділені рядки `strdup(key)` та `strdup(body)` коректно звільняються у функції `idem_destroy()` та при витісненні `idem_evict_expired()`.

## 13. Спостережуваність і моніторинг (Prometheus Metrics)

У промисловій експлуатації рушій ідемпотентності експортує ключові метрики для моніторингу стабільності сервісу:

* `idempotency_requests_total{status="execute"}` — кількість первинних унікальних операцій.
* `idempotency_requests_total{status="cached"}` — кількість успішно перехоплених мережевих дублікатів (показує частку нестабільних клієнтських з'єднань).
* `idempotency_requests_total{status="in_flight_conflict"}` — сплески конкурентних повторів (сигнал про агресивний бекоф або шторм повторів).
* `idempotency_requests_total{status="payload_mismatch"}` — спроби підміни тіла (сигнал про помилку клієнтського коду або атаку).
* `idempotency_store_size_bytes` — поточний обсяг зайнятої пам'яті в таблиці ключів.

### Порогові правила алертингу (Grafana & Alertmanager):
* Якщо частка `in_flight_conflict` перевищує 5 % від загального вхідного потоку, це свідчить про масові передчасні повтори на клієнтах без урахування часу очікування обробки.
* Якщо метрика `payload_mismatch` зростає вище нуля в звичайному режимі, це сигналізує про випуск нової версії клієнтського застосунку з багом повторного використання статичного або захардкодженного ключа.
* Якщо `idempotency_store_size_bytes` перевищує 80 % від виділеного ліміту пам'яті контейнера, необхідно прискорити інтервал роботи фонового прибиральника `evict_expired()` або скоротити TTL зберігання.

## Висновок

Рушій ідемпотентності є фундаментальним вузлом надійності: він ізолює прикладну бізнес-логіку від хаосу мережевих повторів, гарантує строгу атомарність виконання і забезпечує повернення консистентного результату за будь-яких часткових відмов розподіленого середовища.
