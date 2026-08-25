# ⚙️ Реалізація дворівневого когерентного кешу (L1 In-Memory + L2 Redis) з клієнтським трекінгом

Поєднання локального кешу в оперативній пам'яті процесу (L1) та спільного розподіленого кешу (L2 Redis) дозволяє скоротити час відповіді мікросервісу з 1–2 мс до 100 нс, повністю розвантажуючи мережевий інтерфейс і захищаючи центральний кластер Redis від перевантаження за процесорним часом.

Проте локальний кеш у пам'яті процесу небезпечний тим, що кожен екземпляр сервісу живе у власному ізольованому адресному просторі. Якщо екземпляр #1 оновлює запис у базі даних і скидає L2 Redis, екземпляри #2 і #3 не дізнаються про це без спеціального протоколу оповіщення і продовжуватимуть віддавати застарілий стан користувачам.

Нижче наведено повнофункціональну реалізацію дворівневого кешу з підтримкою клієнтського трекінгу, атомарних маркерів оренди (Lease Generation) та захистом від гонок застарілого запису (Stale-Overwrite Races).

## Архітектура та принцип взаємодії шарів

Дворівневий кеш організовано як конвеєр із послідовною ескалацією звернень:

```
[Потік застосунку]
       │
       ▼
 1. Читання з L1 (RAM Map) ──── (Хіт: 0.1 мкс) ───> [Повернення значення]
       │
       ├─ (Промах)
       ▼
 2. Запит у L2 (Redis / Lease) ── (Хіт: 1.5 мс) ──> [Збереження в L1]
       │
       ├─ (Промах)
       ▼
 3. Читання зі СКБД ────────── (50 мс) ─────────> [Атомарний SET з токеном]
```

### Життєвий цикл операцій складається з чотирьох фаз:

1. **Фаза надшвидкого читання (L1 Fast-Path):** Застосунок звертається до локальної хеш-таблиці, захищеної блокуванням читача-письменника (*Reader-Writer Lock*). Якщо ключ присутній, валідний і його час життя не сплив, значення повертається безпосередньо з RAM за 50–100 наносекунд без жодного мережевого виклику чи системного виклику до сокета.
2. **Фаза отримання оренди при промаху (Lease Acquisition):** Якщо ключ відсутній у L1 та L2, кеш-менеджер видає клієнту числовий маркер оренди (*Lease Token*) з монотонного атомарного лічильника. Цей маркер резервує слот і блокує паралельні запити від лавинного шторму (Thundering Herd).
3. **Фаза збереження з валідацією (Lease Validation Set):** Після виконання важкого SQL-запиту в базі даних сервіс намагається поповнити кеш, передаючи отриманий раніше маркер оренди. Якщо за час звернення до СКБД надійшла подія інвалідації або інший запис змінив стан ключа, маркер оренди вважається анульованим, і запис застарілих даних відхиляється.
4. **Фаза асинхронної інвалідації (Push Invalidation Handler):** Окремий фоновий потік слухає вхідні push-повідомлення від сервера Redis (протокол RESP3) або шини подій (Kafka / NATS). Отримавши сповіщення про зміну ключа, слухач захоплює ексклюзивне блокування запису і негайно виставляє прапорець `is_valid = false`, анулюючи активний токен оренди.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>

#define L1_CAPACITY 1024
#define KEY_MAX_LEN 64
#define VAL_MAX_LEN 256

/* Елемент локального L1 кешу в оперативній пам'яті */
typedef struct {
    char key[KEY_MAX_LEN];
    char value[VAL_MAX_LEN];
    uint64_t version;
    uint64_t lease_token;
    time_t expires_at;
    bool is_valid;
} L1Entry;

/* Дворівневий кеш-менеджер */
typedef struct {
    L1Entry table[L1_CAPACITY];
    pthread_rwlock_t lock;
    uint64_t global_lease_counter;
} TwoTierCache;

static unsigned int hash_key(const char *key) {
    unsigned int h = 5381;
    while (*key) {
        h = ((h << 5) + h) + (unsigned char)(*key++);
    }
    return h % L1_CAPACITY;
}

void cache_init(TwoTierCache *c) {
    memset(c->table, 0, sizeof(c->table));
    pthread_rwlock_init(&c->lock, NULL);
    c->global_lease_counter = 1;
}

void cache_destroy(TwoTierCache *c) {
    pthread_rwlock_destroy(&c->lock);
}

/* 1. Швидке читання з L1 кешу */
bool cache_get_l1(TwoTierCache *c, const char *key, char *out_val, size_t out_size, uint64_t *out_ver) {
    unsigned int idx = hash_key(key);
    bool found = false;
    time_t now = time(NULL);

    pthread_rwlock_rdlock(&c->lock);
    if (c->table[idx].is_valid && strcmp(c->table[idx].key, key) == 0) {
        if (c->table[idx].expires_at > now) {
            snprintf(out_val, out_size, "%s", c->table[idx].value);
            if (out_ver) *out_ver = c->table[idx].version;
            found = true;
        }
    }
    pthread_rwlock_unlock(&c->lock);
    return found;
}

/* 2. Обробник асинхронного push-повідомлення інвалідації від Redis/брокера */
void cache_on_invalidation_push(TwoTierCache *c, const char *key, uint64_t min_valid_ver) {
    unsigned int idx = hash_key(key);

    pthread_rwlock_wrlock(&c->lock);
    if (c->table[idx].is_valid && strcmp(c->table[idx].key, key) == 0) {
        if (c->table[idx].version <= min_valid_ver) {
            c->table[idx].is_valid = false;
            c->table[idx].lease_token = 0; /* Анулювання оренди */
        }
    }
    pthread_rwlock_unlock(&c->lock);
}

/* 3. Отримання токена оренди при кеш-промаху */
uint64_t cache_acquire_lease(TwoTierCache *c, const char *key) {
    unsigned int idx = hash_key(key);
    uint64_t token;

    pthread_rwlock_wrlock(&c->lock);
    token = ++c->global_lease_counter;
    snprintf(c->table[idx].key, KEY_MAX_LEN, "%s", key);
    c->table[idx].lease_token = token;
    c->table[idx].is_valid = false;
    pthread_rwlock_unlock(&c->lock);

    return token;
}

/* 4. Запис у кеш із валідацією токена оренди (Захист від Stale-Overwrite) */
bool cache_set_with_lease(TwoTierCache *c, const char *key, const char *val, uint64_t ver, uint64_t token, int ttl_sec) {
    unsigned int idx = hash_key(key);
    bool success = false;

    pthread_rwlock_wrlock(&c->lock);
    /* Запис дозволено тільки якщо токен оренди не був анульований інвалідацією */
    if (strcmp(c->table[idx].key, key) == 0 && c->table[idx].lease_token == token) {
        snprintf(c->table[idx].value, VAL_MAX_LEN, "%s", val);
        c->table[idx].version = ver;
        c->table[idx].expires_at = time(NULL) + ttl_sec;
        c->table[idx].is_valid = true;
        c->table[idx].lease_token = 0; /* Оренду успішно закрито */
        success = true;
    }
    pthread_rwlock_unlock(&c->lock);
    return success;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <shared_mutex>
#include <optional>
#include <chrono>
#include <atomic>
#include <memory>

class TwoTierCoherentCache {
public:
    struct CacheEntry {
        std::string value;
        uint64_t version{0};
        uint64_t lease_token{0};
        std::chrono::steady_clock::time_point expires_at;
        bool is_valid{false};
    };

    explicit TwoTierCoherentCache(std::chrono::seconds default_ttl = std::chrono::seconds(60))
        : default_ttl_(default_ttl), lease_generator_(1) {}

    // 1. Швидке читання з локального L1 кешу (без мережевих затримок)
    [[nodiscard]] std::optional<std::pair<std::string, uint64_t>> 
    get_l1(std::string_view key) const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        auto it = storage_.find(std::string(key));
        if (it == storage_.end() || !it->second.is_valid) {
            return std::nullopt;
        }

        if (std::chrono::steady_clock::now() >= it->second.expires_at) {
            return std::nullopt; // Термін дії сплив
        }

        return std::make_pair(it->second.value, it->second.version);
    }

    // 2. Видача токена оренди при кеш-промаху (Thundering Herd & Stale-Write Protection)
    [[nodiscard]] uint64_t acquire_lease(std::string_view key) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        uint64_t token = lease_generator_.fetch_add(1, std::memory_order_relaxed);
        
        auto& entry = storage_[std::string(key)];
        entry.lease_token = token;
        entry.is_valid = false;
        return token;
    }

    // 3. Збереження результату читання зі СКБД з перевіркою маркеру оренди
    bool set_with_lease(std::string_view key, std::string_view value, 
                        uint64_t version, uint64_t token) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = storage_.find(std::string(key));
        
        // Якщо ключ відсутній або оренду було скасовано паралельною інвалідацією — відхиляємо запис
        if (it == storage_.end() || it->second.lease_token != token) {
            return false;
        }

        it->second.value = std::string(value);
        it->second.version = version;
        it->second.expires_at = std::chrono::steady_clock::now() + default_ttl_;
        it->second.is_valid = true;
        it->second.lease_token = 0; // Оренду успішно використано
        return true;
    }

    // 4. Обробник події інвалідації (Redis RESP3 Tracking / Kafka CDC Topic)
    void on_invalidation(std::string_view key, uint64_t mutated_version) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = storage_.find(std::string(key));
        if (it != storage_.end()) {
            if (it->second.version <= mutated_version) {
                it->second.is_valid = false;
                it->second.lease_token = 0; // Анулювання активної оренди
            }
        }
    }

    // 5. Очищення застарілих елементів
    void purge_expired() {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        const auto now = std::chrono::steady_clock::now();
        for (auto it = storage_.begin(); it != storage_.end(); ) {
            if (!it->second.is_valid || it->second.expires_at <= now) {
                it = storage_.erase(it);
            } else {
                ++it;
            }
        }
    }

private:
    std::chrono::seconds default_ttl_;
    std::atomic<uint64_t> lease_generator_;
    mutable std::shared_mutex mutex_;
    std::unordered_map<std::string, CacheEntry> storage_;
};
```
:::

## Покрокове простеження стану слота під час гонки

Щоб побачити дію протоколу на рівні пам'яті, простежимо переходи полів структури `L1Entry` під час накладання повільного читання на паралельний запис:

1. **Стан 0 (Початковий):** Ключ `user:42` відсутній. Слот: `{key: "", is_valid: false, lease_token: 0, version: 0}`.
2. **Крок 1 (Читач 1: Промах):** Потік 1 викликає `cache_acquire_lease("user:42")`. Слот отримує токен: `{key: "user:42", is_valid: false, lease_token: 101, version: 0}`. Потік 1 іде в базу даних читати баланс 100.
3. **Крок 2 (Письменник 2: Мутація в СКБД):** Потік 2 записує в базу баланс 150 (версія 2) і публікує інвалідацію.
4. **Крок 3 (Слухач інвалідацій):** Фоновий слухач перехоплює повідомлення і викликає `cache_on_invalidation_push("user:42", 2)`. Слот змінює поля: `{key: "user:42", is_valid: false, lease_token: 0, version: 0}`. **Токен 101 скинуто в 0!**
5. **Крок 4 (Читач 1: Спроба запису):** Потік 1 повертається з бази і намагається виконати `cache_set_with_lease("user:42", "100", 1, 101, 60)`. Функція перевіряє умову `lease_token == 101`. Оскільки в слоті значення вже `0`, перевірка дає хибу (`false`), і функція негайно повертає помилку. Застарілі 100 грн не потрапляють у пам'ять!

## Інженерний аналіз продуктивності та тонкощі паралелізму

1. **Конкуренція за блокування (Lock Contention):**
   Використання `pthread_rwlock_t` у C та `std::shared_mutex` у C++ забезпечує практично лінійне масштабування операцій читання. Сотні робочих потоків вебсервера можуть одночасно читати гарячі ключі з L1 без виклику системних перемикань контексту ядра ОС. Ексклюзивне блокування `wrlock` захоплюється лише на 5–15 наносекунд для зміни вказівника або прапорця валідності.
2. **Взаємне блокування при обробці push-інвалідацій (Deadlock in Invalidation Handler):**
   Якщо потік запису в L1 утримує ексклюзивне блокування й одночасно намагається надіслати підтвердження в синхронний сокет брокера, який очікує звільнення іншого ресурсу, настає взаємне блокування. Обробка push-повідомлень має бути суто асинхронною та неблокуючою: сокетний потік лише складає події у вхідну чергу або миттєво інвалідує хеш-таблицю.
3. **Шторм інвалідацій при масових оновленнях (Invalidation Storm):**
   Якщо пакетна міграція бази даних оновлює 500 000 рядків, генерація півмільйона індивідуальних подій інвалідації викличе параліч мережевого інтерфейсу L1-слухачів. Необхідно підтримувати префіксні інвалідації або скидання за шаблоном (наприклад, `EVICT_PATTERN "users:*"`).
4. **Фрагментація пам'яті процесу:**
   Постійне виділення та видалення рядкових об'єктів у локальному L1 кеші призводить до фрагментації купи. У промислових системах рекомендується використовувати арени пам'яті (*Arena Allocators*) або фіксовані байтові буфери з попереднім виділенням.
5. **Інтеграція з клієнтськими бібліотеками:**
   У реальних проєктах на Linux функція `cache_on_invalidation_push` реєструється як зворотний виклик (callback) у бібліотеці `libhiredis` (або `redis-plus-plus` для C++), яка обробляє push-повідомлення в окремому циклі подій `epoll`.
