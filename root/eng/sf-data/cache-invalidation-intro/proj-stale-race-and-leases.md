# ⚙️ Захист від гонки застарілого запису: лізи та токени покоління

Найбільш підступна вразливість патерну Cache-Aside виникає через асинхронне перевпорядкування операцій між паралельними читачами та записувачами.

Коли клієнт отримує промах кешу, він звертається до бази даних, отримує значення `v₁`, але через мережеву затримку або паузу збирача сміття записує його в кеш уже після того, як інший процес оновив базу до `v₂` та видалив старий ключ з кешу. У результаті в базі даних лежить новий стан, а в кеші назавжди застряє старий (примарний запис, ghost entry).

Розв'язанням цієї проблеми є механізм **ліз та токенів покоління** (Leases and Generation Tokens), запропонований інженерами Facebook у системі масштабування Memcached.

## Анатомія вразливості: як виникає примарний запис

У класичній реалізації Cache-Aside розробники застосовують наївну схему взаємодії:
- Під час читання: якщо ключа немає в кеші, прочитати рядок з SQL-бази та виконати `SET key value`.
- Під час запису: оновити рядок у SQL-базі та виконати `DELETE key` у кеші.

На перший погляд здається, що видалення ключа гарантує чистоту: наступний читач побачить порожній кеш і завантажить свіжий стан. Проте в розподілених системах операції виконуються не миттєво. Розглянемо точну послідовність мікросекундних подій між двома незалежними потоками застосунку:

1. **Мілісекунда 0:** Потік А (читач) звертається до кешу за даними користувача `user:42`. Кеш повертає промах (`nil`).
2. **Мілісекунда 2:** Потік А надсилає SQL-запит `SELECT * FROM users WHERE id = 42` до первинної бази даних. База повертає старий запис `name = "Alice"` (версія `v₁`).
3. **Мілісекунда 3:** Потік А потрапляє під раптову паузу середовища виконання — це може бути тривала пауза збирача сміття (GC pause), витіснення потоку планувальником операційної системи або затримка повторної передачі пакета TCP (TCP retransmission timeout). Потік А «засинає» на 150 мілісекунд, тримаючи старе значення `v₁` у своїй локальній пам'яті.
4. **Мілісекунда 10:** Потік Б (записувач) отримує запит від користувача на зміну імені. Він виконує транзакцію `UPDATE users SET name = 'Bob' WHERE id = 42` (версія `v₂`) і успішно фіксує її в базі даних.
5. **Мілісекунда 12:** Потік Б надсилає команду `DELETE user:42` у кеш. Сервер кешу видаляє ключ. Кеш тепер порожній і готовий прийняти нове значення `v₂`.
6. **Мілісекунда 153:** Потік А нарешті «прокидається». Він абсолютно не підозрює, що за час його сну світ змінився, база даних оновилася, а кеш був очищений. Потік А вважає, що успішно завершив читання, і надсилає в кеш команду `SET user:42 "Alice"`.

У цей момент система зазнає катастрофічної розсинхронізації: канонічна база даних містить ім'я `"Bob"`, а кеш — застаріле ім'я `"Alice"`. Усі наступні читачі, які прийдуть через секунду, хвилину чи годину, потраплятимуть у кеш і отримуватимуть застаріле значення `"Alice"`. Цей стан зберігатиметься до наступного оновлення або примусового закінчення TTL.

## Принцип роботи версійних ліз

Замість того, щоб дозволяти будь-якому клієнту записувати довільні дані за командою `SET`, сервер кешу бере процес оновлення під контроль за допомогою 64-бітного токена лізи (*ліза* — від англ. *lease*, тимчасова оренда права на оновлення):

1. **Запит з промахом:** Клієнт звертається за ключем `GET key`. Якщо ключа немає, сервер кешу генерує унікальний числовий токен `lease_token = ++current_generation` і повертає його клієнту разом із сигналом промаху.
2. **Читання з бази:** Клієнт виконує повільний SQL-запит до первинної бази даних, отримуючи значення `v₁`.
3. **Паралельне оновлення:** Якщо в цей момент записувач змінює базу на `v₂` і викликає `DELETE key` (або `INVALIDATE key`), сервер кешу збільшує лічильник покоління ключа `current_generation++`. Усі раніше видані токени для цього ключа автоматично стають недійсними.
4. **Умовний запис:** Читач надсилає команду `SET key, value=v₁, token=lease_token`. Сервер кешу порівнює переданий токен із поточним поколінням ключа. Оскільки покоління змінилося (`lease_token < current_generation`), сервер відхиляє застарілий запис.
5. **Захист від лавини (Stampede):** Якщо протягом дії лізи приходять інші читачі, сервер кешу не видає їм нових ліз, а повертає спеціальний код `TRY_AGAIN` або віддає попереднє застаріле значення (stale-while-revalidate), захищаючи базу даних від шквалу однакових запитів.

## Скінченний автомат стану лізи

Кожен запис у сховищі підпорядковується чіткому життєвому циклу, який описується станами:

- **EMPTY (Порожній):** Запису немає або його було видалено. Будь-який запит на читання переводить стан у `LEASE_GRANTED` і видає перший токен.
- **LEASE_GRANTED (Лізу видано):** Рівно один потік отримав дозвіл піти в базу даних. Інші потоки, які звертаються за цим ключем, отримують відповідь `LEASE_BUSY` і чекають, не навантажуючи базу.
- **VALID (Валідний):** Власник лізи успішно надав свіжі дані. Кеш повертає швидкі відповіді (`CACHE_HIT`).
- **INVALIDATED (Інвалідовано):** Записувач змінив базу даних. Лічильник покоління збільшується, активні лізи анулюються, запис повертається в стан очікування нової лізи.

## Реалізація сховища з підтримкою версійних ліз

Нижче наведено повну реалізацію in-memory кеш-сервера з підтримкою токенів покоління та ліз мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define MAX_KEY_LEN   64
#define MAX_VAL_LEN   256
#define TABLE_SIZE    1024

typedef enum {
    CACHE_HIT,
    CACHE_MISS_LEASE_GRANTED,
    CACHE_MISS_LEASE_BUSY,
    SET_SUCCESS,
    SET_STALE_TOKEN_REJECTED
} cache_status_t;

typedef struct cache_entry {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    bool is_valid;
    uint64_t generation;
    uint64_t active_lease_token;
    time_t lease_expiry;
    struct cache_entry *next;
} cache_entry_t;

typedef struct {
    cache_entry_t *buckets[TABLE_SIZE];
    pthread_mutex_t lock;
    uint64_t global_token_counter;
} lease_cache_t;

static unsigned int hash_key(const char *key) {
    unsigned int hash = 5381;
    while (*key) {
        hash = ((hash << 5) + hash) + (unsigned char)(*key++);
    }
    return hash % TABLE_SIZE;
}

void lease_cache_init(lease_cache_t *cache) {
    memset(cache->buckets, 0, sizeof(cache->buckets));
    pthread_mutex_init(&cache->lock, NULL);
    cache->global_token_counter = 1000;
}

static cache_entry_t* find_or_create_entry(lease_cache_t *cache, const char *key) {
    unsigned int idx = hash_key(key);
    cache_entry_t *entry = cache->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) return entry;
        entry = entry->next;
    }
    entry = (cache_entry_t*)malloc(sizeof(cache_entry_t));
    strncpy(entry->key, key, MAX_KEY_LEN - 1);
    entry->key[MAX_KEY_LEN - 1] = '\0';
    entry->is_valid = false;
    entry->generation = 1;
    entry->active_lease_token = 0;
    entry->lease_expiry = 0;
    entry->next = cache->buckets[idx];
    cache->buckets[idx] = entry;
    return entry;
}

cache_status_t lease_cache_get(lease_cache_t *cache, const char *key, 
                               char *out_val, uint64_t *out_token) {
    pthread_mutex_lock(&cache->lock);
    cache_entry_t *entry = find_or_create_entry(cache, key);
    time_t now = time(NULL);

    if (entry->is_valid) {
        strncpy(out_val, entry->value, MAX_VAL_LEN - 1);
        out_val[MAX_VAL_LEN - 1] = '\0';
        pthread_mutex_unlock(&cache->lock);
        return CACHE_HIT;
    }

    if (entry->active_lease_token != 0 && now < entry->lease_expiry) {
        pthread_mutex_unlock(&cache->lock);
        return CACHE_MISS_LEASE_BUSY;
    }

    entry->active_lease_token = ++cache->global_token_counter;
    entry->lease_expiry = now + 5;
    *out_token = entry->active_lease_token;
    pthread_mutex_unlock(&cache->lock);
    return CACHE_MISS_LEASE_GRANTED;
}

cache_status_t lease_cache_set(lease_cache_t *cache, const char *key, 
                               const char *val, uint64_t token) {
    pthread_mutex_lock(&cache->lock);
    cache_entry_t *entry = find_or_create_entry(cache, key);

    if (entry->active_lease_token != token) {
        pthread_mutex_unlock(&cache->lock);
        return SET_STALE_TOKEN_REJECTED;
    }

    strncpy(entry->value, val, MAX_VAL_LEN - 1);
    entry->value[MAX_VAL_LEN - 1] = '\0';
    entry->is_valid = true;
    entry->active_lease_token = 0;
    entry->generation++;
    pthread_mutex_unlock(&cache->lock);
    return SET_SUCCESS;
}

void lease_cache_invalidate(lease_cache_t *cache, const char *key) {
    pthread_mutex_lock(&cache->lock);
    cache_entry_t *entry = find_or_create_entry(cache, key);
    entry->is_valid = false;
    entry->generation++;
    entry->active_lease_token = 0;
    pthread_mutex_unlock(&cache->lock);
}

void lease_cache_destroy(lease_cache_t *cache) {
    pthread_mutex_lock(&cache->lock);
    for (int i = 0; i < TABLE_SIZE; ++i) {
        cache_entry_t *entry = cache->buckets[i];
        while (entry) {
            cache_entry_t *tmp = entry->next;
            free(entry);
            entry = tmp;
        }
        cache->buckets[i] = NULL;
    }
    pthread_mutex_unlock(&cache->lock);
    pthread_mutex_destroy(&cache->lock);
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <shared_mutex>
#include <mutex>
#include <optional>
#include <chrono>
#include <cstdint>
#include <thread>

enum class CacheGetStatus {
    Hit,
    MissLeaseGranted,
    MissLeaseBusy
};

enum class CacheSetStatus {
    Success,
    StaleTokenRejected
};

struct GetResult {
    CacheGetStatus status;
    std::string value;
    uint64_t token{0};
};

class LeaseCache {
public:
    explicit LeaseCache(std::chrono::seconds lease_duration = std::chrono::seconds(5))
        : lease_ttl_(lease_duration) {}

    GetResult get(std::string_view key) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto& entry = table_[std::string(key)];
        auto now = std::chrono::steady_clock::now();

        if (entry.is_valid) {
            return {CacheGetStatus::Hit, entry.value, 0};
        }

        if (entry.active_lease_token != 0 && now < entry.lease_expiry) {
            return {CacheGetStatus::MissLeaseBusy, "", 0};
        }

        entry.active_lease_token = ++global_token_counter_;
        entry.lease_expiry = now + lease_ttl_;
        return {CacheGetStatus::MissLeaseGranted, "", entry.active_lease_token};
    }

    CacheSetStatus set(std::string_view key, std::string_view value, uint64_t token) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = table_.find(std::string(key));
        if (it == table_.end() || it->second.active_lease_token != token) {
            return CacheSetStatus::StaleTokenRejected;
        }

        auto& entry = it->second;
        entry.value = value;
        entry.is_valid = true;
        entry.active_lease_token = 0;
        ++entry.generation;
        return CacheSetStatus::Success;
    }

    void invalidate(std::string_view key) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = table_.find(std::string(key));
        if (it != table_.end()) {
            it->second.is_valid = false;
            ++it->second.generation;
            it->second.active_lease_token = 0;
        }
    }

private:
    struct Entry {
        std::string value;
        bool is_valid{false};
        uint64_t generation{1};
        uint64_t active_lease_token{0};
        std::chrono::steady_clock::time_point lease_expiry;
    };

    mutable std::shared_mutex mutex_;
    std::unordered_map<std::string, Entry> table_;
    uint64_t global_token_counter_{1000};
    std::chrono::seconds lease_ttl_;
};
```
:::

## Поведінка клієнтського коду та стратегія повторів

Для повноти картини розглянемо, як прикладний код взаємодіє з кешем, що видає лізи. Коли клієнт отримує статус `MissLeaseBusy`, він не повинен негайно бомбардувати базу даних — це зруйнувало б увесь сенс захисту. Замість цього клієнт застосовує цикл очікування з випадковим відступом (backoff and jitter):

:::tabs
```c
char* fetch_user_data(lease_cache_t *cache, const char *key) {
    char buffer[MAX_VAL_LEN];
    uint64_t token = 0;
    int retries = 5;

    while (retries-- > 0) {
        cache_status_t status = lease_cache_get(cache, key, buffer, &token);

        if (status == CACHE_HIT) {
            return strdup(buffer);
        }

        if (status == CACHE_MISS_LEASE_GRANTED) {
            char *db_val = "Alice";
            cache_status_t set_res = lease_cache_set(cache, key, db_val, token);
            if (set_res == SET_STALE_TOKEN_REJECTED) {
                fprintf(stderr, "Попередження: токен застарів, запис відхилено кешем.\n");
            }
            return strdup(db_val);
        }

        if (status == CACHE_MISS_LEASE_BUSY) {
            usleep(20000 + (rand() % 10000));
        }
    }

    return strdup("Alice");
}
```
```cpp
std::string fetchUserData(LeaseCache& cache, std::string_view key) {
    int retries = 5;
    while (retries-- > 0) {
        auto res = cache.get(key);

        if (res.status == CacheGetStatus::Hit) {
            return res.value;
        }

        if (res.status == CacheGetStatus::MissLeaseGranted) {
            std::string db_val = "Alice";
            auto set_res = cache.set(key, db_val, res.token);
            if (set_res == CacheSetStatus::StaleTokenRejected) {
                std::cerr << "Попередження: токен застарів, запис відхилено кешем.\n";
            }
            return db_val;
        }

        if (res.status == CacheGetStatus::MissLeaseBusy) {
            std::this_thread::sleep_for(std::chrono::milliseconds(20 + (std::rand() % 10)));
        }
    }

    return "Alice";
}
```
:::

## Покроковий розбір сценарію гонки

Простежимо, як наведений код обробляє критичну послідовність звернень:

```
[Крок 1] Клієнт 1: get("user:42")
         → Кеш: промах. Видано lease_token = 1001.

[Крок 2] Клієнт 1: виконує повільний SELECT з БД, отримує {"name": "Alice"}.

[Крок 3] Клієнт 2: UPDATE user SET name="Bob" WHERE id=42;
         Клієнт 2: invalidate("user:42")
         → Кеш: generation=2, active_lease_token скинуто в 0.

[Крок 4] Клієнт 1: прокидається й робить set("user:42", "Alice", token=1001)
         → Кеш перевіряє: active_lease_token (0) != token (1001).
         → РЕЗУЛЬТАТ: SET_STALE_TOKEN_REJECTED!
```

Завдяки перевірці токена застарілий запис від Клієнта 1 відкидається, а кеш залишається порожнім до наступного читання, яке прочитає вже актуальне значення `"Bob"`.

## Взаємодія з шардуванням та реплікацією

У великих розподілених кластерах (наприклад, Redis Cluster або Memcached пул з консистентним хешуванням) виникають додаткові виклики узгодження ліз.

### 1. Локальність токенів покоління за консистентним хешуванням

Коли простір ключів розбито на шарди за алгоритмом консистентного хешування (Consistent Hashing), кожен ключ `K` закріплено за конкретним фізичним вузлом кластера.

Оскільки всі операції над ключем `K` (`GET`, `SET`, `INVALIDATE`) потрапляють на той самий вузол, лічильник покоління `generation` і стан лізи не потребують міжвузлового консенсусу (Raft або Paxos). Вузол керує токенами локально в оперативній пам'яті через атомарні операції або м'ютекс.

Проте під час ребалансування або падіння вузла (failover) новий вузол, що перебирає на себе володіння шардом, починає з порожнього стану (`generation = 1`). Усі старі лізи, видані попереднім вузлом, автоматично стають недійсними, що запобігає будь-якому внесенню застарілих даних під час аварійного перемикання.

### 2. Читання з реплік та реплікаційний лаг

Якщо архітектура кешу використовує схему «лідер-репліка» (Leader-Follower) для масштабування читання, читач може натрапити на реплікаційний лаг (Replication Lag):
- Записувач інвалідував ключ на лідері кешу в момент `t₀`.
- Репліка дізнається про інвалідацію лише в момент `t₀ + δ_rep`.
- Якщо клієнт звертається за лізою до репліки, він може отримати застарілий токен.

Щоб уникнути цієї пастки, у Facebook Memcached застосували суворе правило: **усі запити з промахами, що вимагають видачі або перевірки ліз, спрямовуються виключно на лідерний шар сервісу кешування**. Репліки використовуються лише для віддачі гарантовано валідних влучань (`CACHE_HIT`).

## Лізи на читання проти Transactional Outbox на запис

Часто виникає питання: чи замінюють версійні лізи патерни надійного запису, такі як Transactional Outbox або CDC (Change Data Capture)?

Ці два механізми захищають систему з протилежних боків і доповнюють один одного:

- **Transactional Outbox / CDC (захист з боку записувача):** гарантує, що повідомлення про інвалідацію ніколи не загубиться в мережі, якщо транзакція в базі даних була зафіксована. Але CDC ніяк не захищає від того, що паралельний повільний читач запише старий стан після того, як подія CDC видалила ключ.
- **Версійні лізи (захист з боку читача):** гарантують, що жоден запізнілий читач не зможе записати застаріле значення в кеш, навіть якщо він спав хвилину. Проте якщо записувач узагалі забуде надіслати інвалідацію, лізи не допоможуть.

У високонавантажених промислових архітектурах застосовують **синергію обох механізмів**:
1. База даних фіксує зміну та записує подію в Outbox-таблицю.
2. CDC-демон (наприклад, Debezium) читає журнал WAL і надсилає команду `INVALIDATE key` у кеш.
3. Сервер кешу збільшує лічильник покоління ключа.
4. Будь-який читач, що завис під час читання старої версії з бази, отримує відхилення `SET_STALE_TOKEN_REJECTED` завдяки невідповідності токена лізи.

## Реалізація патерну в Redis за допомогою атомарних Lua-скриптів

Хоча наведений C/C++ код демонструє внутрішню будову кеш-рушія, у виробничих бекендах як кеш найчастіше використовують Redis. Стандартні команди Redis (`GET`, `SET`, `DEL`) не підтримують лізи «з коробки», але цей патерн легко реалізується за допомогою атомарних Lua-скриптів (команда `EVAL`), які виконуються в єдиному потоці Redis без ризику гонок.

### 1. Скрипт отримання з видачею лізи (`get_or_lease.lua`)

Скрипт перевіряє наявність ключа, і якщо запис невалідний або відсутній, атомарно створює токен лізи:

```lua
local key = KEYS[1]
local lease_ttl_sec = tonumber(ARGV[1]) or 5

local val = redis.call('HGET', key, 'val')
local is_valid = redis.call('HGET', key, 'valid')

if is_valid == '1' then
    return {'HIT', val, '0'}
end

local active_token = redis.call('HGET', key, 'token')
local now = redis.call('TIME')[1]
local expiry = tonumber(redis.call('HGET', key, 'expiry') or '0')

if active_token and tonumber(now) < expiry then
    return {'BUSY', '', '0'}
end

local next_token = tostring(redis.call('INCR', 'global:lease:counter'))
redis.call('HSET', key, 'token', next_token, 'expiry', tostring(tonumber(now) + lease_ttl_sec), 'valid', '0')

return {'GRANTED', '', next_token}
```

### 2. Скрипт умовного запису за токеном (`set_with_lease.lua`)

Скрипт перевіряє, чи збігається переданий токен із активним токеном ключа:

```lua
local key = KEYS[1]
local val = ARGV[1]
local token = ARGV[2]

local active_token = redis.call('HGET', key, 'token')

if active_token == token then
    redis.call('HSET', key, 'val', val, 'valid', '1', 'token', '')
    redis.call('HDEL', key, 'expiry')
    return 1 -- Успішний запис
else
    return 0 -- Відхилено: токен застарів (stale token)
end
```

### 3. Скрипт атомарної інвалідації (`invalidate.lua`)

```lua
local key = KEYS[1]
redis.call('HSET', key, 'valid', '0', 'token', '')
redis.call('HDEL', key, 'expiry')
return 1
```

Використання Lua-скриптів гарантує атомарність перевірки та запису на рівні рушія Redis, усуваючи необхідність у розподілених блокуваннях (Redlock) для захисту від гонок інвалідації.

## Лізи проти патерну Stale-While-Revalidate

У практичних архітектурах існує вибір між жорстким блокуванням застарілих записів (Leases) та м'яким обслуговуванням застарілих відповідей (Stale-While-Revalidate, SWR):

1. **Суворі лізи (Leases):**
   - *Поведінка:* Якщо ключ інвалідовано, клієнти або чекають, або отримують відмову, поки власник лізи не оновить стан.
   - *Сфера застосування:* Фінансові операції, залишки товарів під час розпродажу, квитки на події, права доступу.
   - *Перевага:* Нульовий ризик показати клієнту скасовану або нечинну інформацію.

2. **М'яке оновлення (Stale-While-Revalidate):**
   - *Поведінка:* Поки фоновий воркер оновлює значення в базі даних, усі паралельні клієнти негайно отримують попереднє значення з позначкою `stale`.
   - *Сфера застосування:* Стрічки новин, коментарі, публічні профілі, каталог товарів у спокійному режимі.
   - *Перевага:* Відсутність затримок (нульова латентність для користувача) та абсолютний захист бази даних від лавини.

## Метрики та телеметрія системи ліз

Для експлуатації кешу з лізами у виробничому середовищі необхідно збирати та моніторити такі ключові метрики (Prometheus / Grafana):

- `cache_leases_granted_total`: Темп видачі нових ліз на промахах. Збігається з частотою холодних звернень до бази даних.
- `cache_leases_busy_total`: Кількість запитів, які зіткнулися з зайнятою лізою й пішли на очікування (backoff). Високе значення свідчить про ефективний захист бази від лавини запитів (Stampede).
- `cache_stale_tokens_rejected_total`: Кількість спроб записати застарілий стан, які були успішно заблоковані кешем. Сплеск цієї метрики вказує на наявність повільних SQL-запитів, де читачі не встигають за темпом записів.
- `cache_lease_timeouts_total`: Кількість випадків, коли клієнт узяв лізу, але не повернувся до закінчення `lease_expiry` (свідчить про збої клієнтських процесів або перевантаження бази).

## Тестування та верифікація гонок у CI/CD

Виявити гонки інвалідації під час звичайного юніт-тестування майже неможливо, оскільки в локальному середовищі звернення до in-memory кешу та тестової бази даних виконуються за частки мілісекунди без мережевих затримок.

Для надійної верифікації механізму ліз у конвеєрах CI/CD застосовують два підходи:

1. **Інжекція штучних затримок (Fault Injection / Jitter):**
   У тестовий мок-клієнт вбудовують випадкові затримки перед відправкою `set()` (від 50 до 300 мс). Запуск 10 000 паралельних операцій читання та запису за наївної схеми без ліз у 100% випадків призводить до розсинхронізації стану. Реалізація з токенами покоління успішно проходить цей тест без жодного отруєного запису.

2. **Запуск під ThreadSanitizer (TSan):**
   Компіляція C/C++ коду з прапорцями `-fsanitize=thread -g` дозволяє перевірити відсутність гонок пам'яті (data races) всередині самого кеш-сервера під час паралельної модифікації хеш-таблиці та лічильників поколінь.

## Чекліст готовності до промислової експлуатації

Перед розгортанням кешування на основі версійних ліз у виробничому середовищі перевірте:

- [ ] Усі обчислення строків дії ліз використовують монотонний таймер (`steady_clock`), а не настінний час (`system_clock`).
- [ ] Тривалість лізи налаштована щонайменше як `3 · p99` затримки первинної бази даних.
- [ ] Клієнтський код реалізує експоненційний відступ із джитером під час отримання статусу `LEASE_BUSY`.
- [ ] Метрика `stale_tokens_rejected` підключена до системи сповіщень (алертів) для виявлення деградації бази даних.
- [ ] Для багатошардових кластерів запити на отримання ліз маршрутизуються виключно на шард-власник ключа за консистентним хешем.

## Інженерні підводні камені та крайові випадки

1. **Зависання або аварія власника лізи:**
   Якщо клієнт отримав токен лізи, але впав під час очікування відповіді від бази даних (crash-stop), ліза не повинна блокувати ключ навічно. Механізм `lease_expiry` гарантує, що після завершення таймера (наприклад, через 5 секунд) наступний клієнт, що отримає статус `CACHE_MISS_LEASE_BUSY`, зможе автоматично перехопити лізу й повторити спробу завантаження.

2. **Вибір тривалості лізи (`lease_ttl`):**
   Якщо ліза занадто коротка (наприклад, 50 мс), а база даних під навантаженням відповідає за 100 мс, ліза встигне протухнути до завершення запиту. Клієнт отримає відмову `StaleTokenRejected`, а кеш ніколи не прогріється. Практичне правило: строк дії лізи повинен перевищувати 99-й перцентиль затримки бази даних щонайменше у 3 рази (`lease_ttl ≥ 3 · p99_db_latency`).

3. **Стійкість годинників (Monotonic Clock):**
   Для обчислення строків ліз категорично заборонено використовувати системний настінний час (`gettimeofday` або `std::chrono::system_clock`). Будь-яка синхронізація через NTP зі стрибком часу назад може призвести до того, що активні лізи залишатимуться зайнятими роками. Слід застосовувати виключно монотонні таймери (`clock_gettime(CLOCK_MONOTONIC)` у C або `std::chrono::steady_clock` у C++).

4. **Накладні витрати пам'яті:**
   Збереження 64-бітного токена, лічильника поколінь та мітки часу додає 24–32 байти метаданих на кожен ключ. Для кешу з 10 мільйонами ключів це вимагає додаткових 250–320 МБ оперативної пам'яті, що є незначною платою за стовідсоткову гарантію захисту від розсинхронізації двох джерел правди.


