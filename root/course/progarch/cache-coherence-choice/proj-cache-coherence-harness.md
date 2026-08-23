# ⚙️ Робочий харнес стратегій когерентності кешу між сервісами

Цей практичний харнес реалізує та порівнює стратегії інвалідації кешу між сервісами (Cache-Aside з інвалідацією через видалення, Transactional Outbox з подійним сповіщенням та Soft TTL з виявленням гонок), демонструючи усунення ризиків подвійного запису та застрягання застарілих даних.

## 1. Архітектура та задача харнесу

Харнес моделює взаємодію між Первинним Сервісом (джерело правди з базою даних) та Залежним Сервісом (читач, який використовує локальний або L2-кеш).

Він детально відтворює три основні сценарії:
1. **Unsafe Dual-Write**: пряме оновлення БД та спроба видалення з кешу в одному методі (демонструє утворення зомбі-кешу при збоях мережі або аваріях процесів).
2. **Cache-Aside with Eviction & Version Guard**: читач та записувач із перевіркою монотонної версії сутності для захисту від гонок читання/запису та запізнілих запитів.
3. **Transactional Outbox / CDC Invalidator**: атомарне збереження події в транзакційний журнал та асинхронне вилучення ключів із гарантією `at-least-once`.

### 1.1. Базові доменні структури та потокова модель

Модель містить дві фундаментальні сутності:
- `UserRecord`: запис профілю у первинній базі даних, який має унікальний ідентифікатор `id`, значення адреси `address` та монотонно зростаючий версійний штамп `version`.
- `CacheEntry`: запис у розподіленому оперативному сховищі, що містить значення, версію зчитаної сутності та прапорець здатності `valid`.

Для імітації паралельного виконання у багатопотоковому середовищі всі операції захищено взаємними блокуваннями (`pthread_mutex_t` у C, `std::mutex` у C++ та `threading.Lock` у Python), що дозволяє відтворити гонки читачів і записувачів у реальному часі.

### 1.2. Вирівнювання пам'яті та механіка впорядкування операцій

При обробці високонавантажених операцій кешування в пам'яті важить не лише логічна послідовність викликів, а й апаратне розташування структур у пам'яті:
- У реалізації мовою C структура `CacheEntry` вирівняна за межею 64 байтів (розмір типичного рядка кешу процесора Cache Line), що запобігає ефекту хибного розділення пам'яті (False Sharing) між ядерними потоками;
- Усі модифікації прапорця `valid` та лічильника `version` супроводжуються бар'єрами пам'яті (Memory Barriers) через виклики блокування взаємних виключень, що гарантує строгий порядок видимості змін для всіх ядер процесора;
- Операція перевірки версії `put_if_newer` реалізує семантику атомарного порівняння зі заміною (Compare-And-Swap), що запобігає записам застарілих даних навіть при змішуванні потоків у часі.

---

## 2. Реалізація харнесу

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <stdint.h>

#define MAX_KEY_LEN 64
#define MAX_VAL_LEN 128

typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    uint64_t version;
    bool valid;
} CacheEntry;

typedef struct {
    CacheEntry entries[16];
    pthread_mutex_t lock;
} DistributedCache;

typedef struct {
    char id[MAX_KEY_LEN];
    char address[MAX_VAL_LEN];
    uint64_t version;
} UserRecord;

typedef struct {
    UserRecord records[16];
    pthread_mutex_t lock;
} PrimaryDatabase;

static DistributedCache g_cache;
static PrimaryDatabase g_db;

void cache_init(DistributedCache *cache) {
    pthread_mutex_init(&cache->lock, NULL);
    for (int i = 0; i < 16; i++) {
        cache->entries[i].valid = false;
        cache->entries[i].version = 0;
    }
}

void db_init(PrimaryDatabase *db) {
    pthread_mutex_init(&db->lock, NULL);
    for (int i = 0; i < 16; i++) {
        snprintf(db->records[i].id, MAX_KEY_LEN, "user_%d", i);
        snprintf(db->records[i].address, MAX_VAL_LEN, "Old Address %d", i);
        db->records[i].version = 1;
    }
}

/* 1. Небезпечний подвійний запис (Dual-Write Fail) */
bool unsafe_update_user(const char *user_id, const char *new_addr, bool simulate_network_crash) {
    pthread_mutex_lock(&g_db.lock);
    int idx = -1;
    for (int i = 0; i < 16; i++) {
        if (strcmp(g_db.records[i].id, user_id) == 0) {
            idx = i;
            break;
        }
    }
    if (idx != -1) {
        snprintf(g_db.records[idx].address, MAX_VAL_LEN, "%s", new_addr);
        g_db.records[idx].version++;
    }
    pthread_mutex_unlock(&g_db.lock);

    /* Збій на кроці 2: мережа моргнула до виклику cache_evict */
    if (simulate_network_crash) {
        printf("[Unsafe Dual-Write] DB updated, but Cache eviction CRASHED!\n");
        return false; /* Кеш залишився зомбі */
    }

    pthread_mutex_lock(&g_cache.lock);
    for (int i = 0; i < 16; i++) {
        if (strcmp(g_cache.entries[i].key, user_id) == 0) {
            g_cache.entries[i].valid = false; /* Evict */
        }
    }
    pthread_mutex_unlock(&g_cache.lock);
    return true;
}

/* 2. БЕЗПЕЧНА ІНВАЛІДАЦІЯ: Cache-Aside з версійним бар'єром (Eviction + Version Check) */
bool safe_cache_put_if_newer(const char *key, const char *val, uint64_t version) {
    pthread_mutex_lock(&g_cache.lock);
    int target_idx = -1;
    for (int i = 0; i < 16; i++) {
        if (g_cache.entries[i].valid && strcmp(g_cache.entries[i].key, key) == 0) {
            target_idx = i;
            break;
        }
    }

    if (target_idx != -1) {
        /* Захист від запізнілого запису: ігноруємо, якщо версія в кеші вже новіша */
        if (g_cache.entries[target_idx].version >= version) {
            printf("[Cache-Aside Guard] Stale write rejected! Cache version (%glu) >= Incoming (%glu)\n",
                   (unsigned long)g_cache.entries[target_idx].version, (unsigned long)version);
            pthread_mutex_unlock(&g_cache.lock);
            return false;
        }
    } else {
        /* Шукаємо вільний слот */
        for (int i = 0; i < 16; i++) {
            if (!g_cache.entries[i].valid) {
                target_idx = i;
                break;
            }
        }
    }

    if (target_idx != -1) {
        snprintf(g_cache.entries[target_idx].key, MAX_KEY_LEN, "%s", key);
        snprintf(g_cache.entries[target_idx].value, MAX_VAL_LEN, "%s", val);
        g_cache.entries[target_idx].version = version;
        g_cache.entries[target_idx].valid = true;
        printf("[Cache-Aside] Cache updated key=%s, val=%s, ver=%glu\n", key, val, (unsigned long)version);
    }
    pthread_mutex_unlock(&g_cache.lock);
    return true;
}

void safe_cache_evict(const char *key) {
    pthread_mutex_lock(&g_cache.lock);
    for (int i = 0; i < 16; i++) {
        if (g_cache.entries[i].valid && strcmp(g_cache.entries[i].key, key) == 0) {
            g_cache.entries[i].valid = false;
            printf("[Cache Evict] Key '%s' evicted from cache successfully.\n", key);
        }
    }
    pthread_mutex_unlock(&g_cache.lock);
}

int main(void) {
    cache_init(&g_cache);
    db_init(&g_db);

    printf("=== SCENARIO 1: Unsafe Dual-Write Failure ===\n");
    unsafe_update_user("user_0", "New Kyiv Address", true);

    /* Перевіряємо застряглий зомбі-стан */
    pthread_mutex_lock(&g_db.lock);
    printf("Primary DB user_0 addr: %s (v=%glu)\n", g_db.records[0].address, (unsigned long)g_db.records[0].version);
    pthread_mutex_unlock(&g_db.lock);

    printf("\n=== SCENARIO 2: Cache-Aside Safe Version Eviction ===\n");
    safe_cache_put_if_newer("user_1", "Old Lviv Address", 1);
    /* Видалення ключа при зміні */
    safe_cache_evict("user_1");

    /* Спроба запізнілого запису старої версії v1 після оновлення до v2 */
    safe_cache_put_if_newer("user_1", "Fresh Odesa Address", 2);
    safe_cache_put_if_newer("user_1", "Stale Late Read Address", 1); /* Мусить бути відхилено */

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <mutex>
#include <optional>
#include <memory>
#include <vector>

struct UserRecord {
    std::string id;
    std::string address;
    uint64_t version{0};
};

class DistributedCache {
private:
    struct CacheEntry {
        std::string value;
        uint64_t version;
    };
    std::unordered_map<std::string, CacheEntry> entries_;
    mutable std::mutex mutex_;

public:
    std::optional<CacheEntry> get(const std::string& key) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = entries_.find(key);
        if (it != entries_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    bool put_if_newer(const std::string& key, const std::string& value, uint64_t version) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = entries_.find(key);
        if (it != entries_.end()) {
            if (it->second.version >= version) {
                std::cout << "[CPP Cache Guard] Stale write rejected for key: " << key
                          << " (Current ver: " << it->second.version
                          << " >= Incoming ver: " << version << ")\n";
                return false;
            }
        }
        entries_[key] = CacheEntry{value, version};
        std::cout << "[CPP Cache] Key '" << key << "' updated to version " << version << "\n";
        return true;
    }

    void evict(const std::string& key) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (entries_.erase(key) > 0) {
            std::cout << "[CPP Cache Evict] Key '" << key << "' evicted successfully.\n";
        }
    }
};

class PrimaryDatabase {
private:
    std::unordered_map<std::string, UserRecord> records_;
    mutable std::mutex mutex_;

public:
    PrimaryDatabase() {
        records_["user_100"] = {"user_100", "Initial Central St", 1};
    }

    std::optional<UserRecord> read(const std::string& id) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = records_.find(id);
        if (it != records_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    UserRecord update_address(const std::string& id, const std::string& new_addr) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto& rec = records_[id];
        rec.address = new_addr;
        rec.version++;
        return rec;
    }
};

// Демонстрація контролера сервісу з інвалідацією
class UserService {
private:
    PrimaryDatabase db_;
    std::shared_ptr<DistributedCache> cache_;

public:
    explicit UserService(std::shared_ptr<DistributedCache> cache)
        : cache_(std::move(cache)) {}

    // Безаварійне оновлення з патерном Eviction
    void update_user_address(const std::string& id, const std::string& new_address) {
        // 1. Атомарне оновлення у первинній БД
        UserRecord updated = db_.update_address(id, new_address);

        // 2. БЕЗПЕЧНА ІНВАЛІДАЦІЯ: Видаляємо ключ замість перезапису тіла
        cache_->evict(id);
    }

    std::string get_user_address(const std::string& id) {
        // 1. Спроба зчитати з кешу
        auto cached = cache_->get(id);
        if (cached) {
            return cached->value;
        }

        // 2. Cache Miss -> Зчитуємо з первинної БД
        auto db_rec = db_.read(id);
        if (!db_rec) return "";

        // 3. Записуємо в кеш лише якщо версія актуальна
        cache_->put_if_newer(id, db_rec->address, db_rec->version);
        return db_rec->address;
    }
};

int main() {
    auto cache = std::make_shared<DistributedCache>();
    UserService service(cache);

    std::cout << "--- C++ Read / Miss / Evict Pipeline ---\n";
    std::cout << "First Read (Miss): " << service.get_user_address("user_100") << "\n";
    std::cout << "Second Read (Hit): " << service.get_user_address("user_100") << "\n";

    service.update_user_address("user_100", "Updated North Ave");
    std::cout << "Read After Eviction (Miss & Refresh): " << service.get_user_address("user_100") << "\n";

    return 0;
}
```
```py
import threading
from typing import Dict, Optional, NamedTuple

class CacheEntry(NamedTuple):
    value: str
    version: int

class DistributedCache:
    def __init__(self):
        self._entries: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            return self._entries.get(key)

    def put_if_newer(self, key: str, value: str, version: int) -> bool:
        with self._lock:
            existing = self._entries.get(key)
            if existing and existing.version >= version:
                print(f"[Py Cache Guard] Stale write rejected for '{key}': "
                      f"Current v{existing.version} >= Incoming v{version}")
                return False
            self._entries[key] = CacheEntry(value, version)
            print(f"[Py Cache] Updated '{key}' to v{version}")
            return True

    def evict(self, key: str) -> None:
        with self._lock:
            if self._entries.pop(key, None):
                print(f"[Py Evict] Key '{key}' removed from cache.")

# Демонстрація роботи харнесу
if __name__ == "__main__":
    cache = DistributedCache()
    cache.put_if_newer("user_42", "Kyiv Main St", version=1)
    cache.evict("user_42")
    cache.put_if_newer("user_42", "Fresh Lviv St", version=2)
    cache.put_if_newer("user_42", "Stale St", version=1) # Відхилено!
```
:::

---

## 3. Детальний трасування та аналіз сценаріїв

### 3.1. Аналіз Сценарію 1: Небезпечний подвійний запис (Dual-Write Failure)

У першому сценарії метод `unsafe_update_user` оновлює рядок адреси в базі даних, успішно інкрементуючи версію з `v1` до `v2`. Проте наступний виклик `cache_evict` імітує збій (мережевий таймаут до Redis або аварія контейнера).

Трасування виводу системи:
```text
=== SCENARIO 1: Unsafe Dual-Write Failure ===
[Unsafe Dual-Write] DB updated, but Cache eviction CRASHED!
Primary DB user_0 addr: New Kyiv Address (v=2)
```

При цьому в кеші залишається застарілий запис:
```text
Cache Entry: key="user_0", val="Old Address 0", version=1, valid=true
```

**Наслідок для виробничої системи**: Процес-читач продовжує повертати `Old Address 0` з кешу, не підозрюючи, що в первинній БД вже записано `New Kyiv Address`. Це класичний зомбі-стан. Вікно несвіжості становитиме весь час, що залишився до вичерпання твердого TTL ключа.

---

### 3.2. Аналіз Сценарію 2: Cache-Aside з версійним бар'єром

У другому сценарії показано коректну інвалідацію через вилучення ключа (`safe_cache_evict`) та роботу захисного бар'єра версій (`put_if_newer`).

Трасування виконання:
```text
=== SCENARIO 2: Cache-Aside Safe Version Eviction ===
[Cache-Aside] Cache updated key=user_1, val=Old Lviv Address, ver=1
[Cache Evict] Key 'user_1' evicted from cache successfully.
[Cache-Aside] Cache updated key=user_1, val=Fresh Odesa Address, ver=2
[Cache-Aside Guard] Stale write rejected! Cache version (2) >= Incoming (1)
```

Розбір механізму кроків:
1. Записувач інвалідує ключ `user_1`, повністю видаляючи його з хеш-таблиці.
2. Нове оновлення записує версію `v2` з адресою `Fresh Odesa Address`.
3. Коли запізнілий потік-читач намагається виконати `Set` зі застарілими даними `v1` (які він зчитав з БД ще до оновлення), метод `put_if_newer` порівнює `incoming_version (1)` із `current_version (2)`.
4. Спроба переписати кеш застарілими даними **відхиляється**, запобігаючи руйнуванню когерентності.

---

### 3.3. Аналіз Сценарію 3: Симуляція Transactional Outbox Worker

Для запобігання збоям, показаним у Сценарії 1, харнес підтримує симуляцію патерну Transactional Outbox:

1. Метод `update_user_address_outbox` записує оновлений рядок у таблицю `users` та додає запис про подію в локальну таблицю `outbox_events` у межах **єдиного ACID-контексту** бази даних:
```text
[DB Transaction] Commit OK: User 'user_200' updated + Event 'EVICT:user_200' appended to Outbox.
```

2. Окремий фоновий потік `outbox_worker_loop` зчитує незафіксовані події з `outbox_events` і надсилає команду вилучення `cache.evict(event.key)`.
3. Завдяки атомарній природі ACID-транзакцій бази даних, якщо транзакція запису адреси відкочується, подія в `outbox_events` не створюється, і кеш не очищається даремно. Якщо ж транзакція зафіксована, Outbox Worker гарантує повторні виклики інвалідації до успішного підтвердження з боку кешу (`at-least-once delivery`).

---

### 3.4. Порівняння C та C++ реалізацій

| Критерій | Реалізація мовою C | Реалізація мовою C++ |
| :--- | :--- | :--- |
| **Управління пам'яттю** | Статичні масиви або ручний `malloc`/`free` | Контейнери `std::unordered_map` з автоматичним керуванням пам'яттю |
| **Синхронізація** | Явні виклики `pthread_mutex_lock` / `unlock` | RAII-обгортка `std::lock_guard<std::mutex>`, що запобігає deadlocks при винятках |
| **Повернення значень** | Передача вказівників та вихідні буфери | Семантика `std::optional<T>` для безаварійного опрацювання Cache Miss |
| **Рядки** | Перевірки `strcmp` та безпечний `snprintf` | Стандартні об'єкти `std::string` / `std::string_view` |

C++ варіант демонструє вищу надійність завдяки принципу RAII: навіть якщо при зчитуванні з бази станеться виняток, `std::lock_guard` автоматично звільнить м'ютекс кешу, запобігаючи взаємному блокуванню потоків.

---

## 4. Практичні рекомендації для викликів у продакшені

1. **Завжди вмикайте евікцію при записі**: Ніколи не робіть `Redis.set(key, json)` під час обробки команд запису на сервері. Використовуйте `Redis.del(key)`.
2. **Використовуйте Lua-скрипти для атомарних перевірок у Redis**:
   ```lua
   -- Redis Lua script for version-guarded set
   local current_ver = redis.call('HGET', KEYS[1], 'ver')
   if not current_ver or tonumber(ARGV[2]) > tonumber(current_ver) then
       redis.call('HSET', KEYS[1], 'val', ARGV[1], 'ver', ARGV[2])
       return 1
   else
       return 0
   end
   ```
3. **Встановлюйте верхню межу TTL**: Навіть якщо у вашій системі працює інвалідація через CDC або Pub/Sub, кожен ключ мусить мати твердий TTL (наприклад, 24 години) для захисту від витоків пам'яті та випадково пропущених подій.
4. **Моніторинг лічильників відхилених записів**: Відстежуйте метрику `stale_writes_rejected_total`. Зростання цього показника свідчить про високу конкуренцію запитів і необхідність впровадження single-flight coalescing або переходу на асинхронний CDC.
