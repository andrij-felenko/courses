# ⚙️ Стійкий клієнт кешування: поєднання захисних тактик у коді

Типові бібліотеки кешування обмежуються примітивними операціями `get(key)` та `set(key, value, ttl)`. За такої наївної реалізації весь тягар захисту від лавиноподібного вичерпання TTL, сканування неіснуючих ідентифікаторів та затримок синхронного оновлення перекладається на прикладного розробника, де він неминуче ігнорується або реалізується з критичними помилками конкурентності.

Цей проектний розділ демонструє побудову завершеного, потокобезпечного клієнта кешування, який на рівні ядра поєднує чотири захисні тактики:
1. **Випадковий розкид часу життя (TTL Jitter)** — усуває синхронізацію видалення ключів;
2. **Кешування порожнечі (Negative Caching)** — захищає базу даних від сканування неіснуючих ідентифікаторів (Cache Penetration);
3. **Дворівневий життєвий цикл (Soft TTL та Hard TTL)** із патерном **Stale-While-Revalidate** — клієнт отримує дані з кешу миттєво, а оновлення виконується у фоні;
4. **Об'єднання запитів (Single-Flight)** для фонового оновлення — запобігає дублюванню викликів до первинного сховища.

## 1. Архітектура та життєвий цикл запису

Структура запису в оперативній пам'яті кешу містить обов'язкові поля для відстеження часових меж та стану синхронізації:
- `value` — корисні закешовані дані;
- `is_negative` — прапорець порожнього результату (сутності немає в базі даних, повернено 404);
- `soft_expiry` — часова мітка, після якої значення вважається застарілим і потребує фонового оновлення;
- `hard_expiry` — часова мітка, після якої значення фізично виселяється з пам'яті;
- `is_refreshing` — атомарний прапорець активного фонового рейсу оновлення.

Часова шкала розділяє життя запису на три чіткі інтервали:

```
+-----------------------------------------------------------------------+
| Свіжі дані (Fresh)  | Застарілі (Stale-While-Revalidate) | Вичерпано  |
+---------------------+------------------------------------+------------+
0                  Soft TTL                             Hard TTL      Час (t)
  [Читання: 0.5 мс]     [Читання: 0.5 мс + Фоновий рейс]   [Блокуючий промах]
```

Під час читання алгоритм перевіряє стан запису в такому порядку:
1. **Поточний час `t < Soft TTL`**: Значення є свіжим (Fresh Hit). Дані негайно повертаються клієнту.
2. **Поточний час `Soft TTL ≤ t < Hard TTL`**: Значення є застарілим, але придатним для використання (Stale Hit). Якщо прапорець `is_refreshing == false`, клієнт атомарно встановлює його в `true` та асинхронно запускає фоновий потік оновлення з первинного джерела. Клієнтський запит негайно отримує закешоване значення без жодного очікування на базу даних.
3. **Поточний час `t ≥ Hard TTL` або ключ відсутній**: Синхронний промах (Hard Miss). Потік блокується, виконує запит до первинного джерела, зберігає нове значення з обчисленим розкидом часу життя (Jitter) і повертає результат клієнту.

## 2. Реалізація клієнта стійкого кешування

Приклад наведено мовами C та C++ у вигляді повноцінного клієнтського модуля.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>

#define MAX_KEY_LEN 128
#define MAX_VAL_LEN 512
#define HASH_SIZE 1024

/* Отримання поточного монотонного часу в секундах */
static double get_monotonic_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

/* Генерація випадкового розкиду (TTL Jitter) у межах ±jitter_ratio */
static double apply_jitter(double base_ttl, double jitter_ratio) {
    double r = ((double)rand() / (double)RAND_MAX) * 2.0 - 1.0; /* [-1.0, 1.0] */
    return base_ttl * (1.0 + r * jitter_ratio);
}

typedef struct CacheEntry {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    bool is_negative;       /* Чи є це кешуванням відсутності (null) */
    double soft_expiry;     /* Час початку фонового оновлення */
    double hard_expiry;     /* Час повного виселення з пам'яті */
    bool is_refreshing;     /* Прапорець активного фонового оновлення */
    struct CacheEntry* next;
} CacheEntry;

typedef struct ResilientCache {
    CacheEntry* buckets[HASH_SIZE];
    pthread_mutex_t locks[HASH_SIZE];
    double default_ttl;
    double soft_ratio;      /* Частка від TTL для Soft Expiry (наприклад 0.75) */
    double negative_ttl;    /* Час життя для порожніх відповідей */
    double jitter_ratio;    /* Коефіцієнт розкиду (наприклад 0.15) */
} ResilientCache;

/* Проста геш-функція djb2 для ключів */
static unsigned int hash_key(const char* str) {
    unsigned long hash = 5381;
    int c;
    while ((c = *str++)) hash = ((hash << 5) + hash) + c;
    return (unsigned int)(hash % HASH_SIZE);
}

ResilientCache* cache_create(double default_ttl, double negative_ttl, double jitter_ratio) {
    ResilientCache* c = (ResilientCache*)malloc(sizeof(ResilientCache));
    if (!c) return NULL;
    c->default_ttl = default_ttl;
    c->soft_ratio = 0.75;
    c->negative_ttl = negative_ttl;
    c->jitter_ratio = jitter_ratio;
    for (int i = 0; i < HASH_SIZE; ++i) {
        c->buckets[i] = NULL;
        pthread_mutex_init(&c->locks[i], NULL);
    }
    return c;
}

/* Збереження запису з розрахунком Soft/Hard TTL та джиттером */
void cache_set(ResilientCache* c, const char* key, const char* val, bool is_neg) {
    unsigned int h = hash_key(key);
    double now = get_monotonic_time();
    double base = is_neg ? c->negative_ttl : c->default_ttl;
    double actual_ttl = apply_jitter(base, c->jitter_ratio);

    pthread_mutex_lock(&c->locks[h]);
    CacheEntry* curr = c->buckets[h];
    while (curr) {
        if (strcmp(curr->key, key) == 0) {
            if (val) {
                strncpy(curr->value, val, MAX_VAL_LEN - 1);
                curr->value[MAX_VAL_LEN - 1] = '\0';
            } else {
                curr->value[0] = '\0';
            }
            curr->is_negative = is_neg;
            curr->soft_expiry = now + (actual_ttl * c->soft_ratio);
            curr->hard_expiry = now + actual_ttl;
            curr->is_refreshing = false;
            pthread_mutex_unlock(&c->locks[h]);
            return;
        }
        curr = curr->next;
    }

    /* Створення нового елемента */
    CacheEntry* entry = (CacheEntry*)malloc(sizeof(CacheEntry));
    if (!entry) {
        pthread_mutex_unlock(&c->locks[h]);
        return;
    }
    strncpy(entry->key, key, MAX_KEY_LEN - 1);
    entry->key[MAX_KEY_LEN - 1] = '\0';
    if (val) {
        strncpy(entry->value, val, MAX_VAL_LEN - 1);
        entry->value[MAX_VAL_LEN - 1] = '\0';
    } else {
        entry->value[0] = '\0';
    }
    entry->is_negative = is_neg;
    entry->soft_expiry = now + (actual_ttl * c->soft_ratio);
    entry->hard_expiry = now + actual_ttl;
    entry->is_refreshing = false;
    entry->next = c->buckets[h];
    c->buckets[h] = entry;
    pthread_mutex_unlock(&c->locks[h]);
}

/* Контекст для фонового потоку оновлення */
typedef struct AsyncArgs {
    ResilientCache* cache;
    char key[MAX_KEY_LEN];
    char* (*loader_fn)(const char* k, bool* not_found);
} AsyncArgs;

static void* async_refresh_worker(void* arg) {
    AsyncArgs* args = (AsyncArgs*)arg;
    bool not_found = false;
    char* fresh_val = args->loader_fn(args->key, &not_found);

    cache_set(args->cache, args->key, fresh_val, not_found);

    if (fresh_val) free(fresh_val);
    free(args);
    return NULL;
}

/* Отримання значення з кешу з автоматичною фоновою ревалідацією */
bool cache_get_or_load(ResilientCache* c, const char* key,
                       char* out_val, size_t out_len,
                       char* (*loader_fn)(const char* k, bool* not_found)) {
    unsigned int h = hash_key(key);
    double now = get_monotonic_time();

    pthread_mutex_lock(&c->locks[h]);
    CacheEntry* curr = c->buckets[h];
    while (curr) {
        if (strcmp(curr->key, key) == 0) {
            /* Перевірка Hard TTL (чи не виселено значення) */
            if (now < curr->hard_expiry) {
                if (curr->is_negative) {
                    /* Знайдено закешовану порожнечу (Negative Hit) */
                    pthread_mutex_unlock(&c->locks[h]);
                    return false; /* 404 Not Found */
                }
                strncpy(out_val, curr->value, out_len - 1);
                out_val[out_len - 1] = '\0';

                /* Перевірка Soft TTL: якщо застаріло і ще не оновлюється */
                if (now >= curr->soft_expiry && !curr->is_refreshing) {
                    curr->is_refreshing = true; /* Захоплюємо рейс */
                    pthread_mutex_unlock(&c->locks[h]);

                    AsyncArgs* args = (AsyncArgs*)malloc(sizeof(AsyncArgs));
                    if (args) {
                        args->cache = c;
                        strncpy(args->key, key, MAX_KEY_LEN - 1);
                        args->loader_fn = loader_fn;
                        pthread_t t;
                        pthread_create(&t, NULL, async_refresh_worker, args);
                        pthread_detach(t);
                    }
                    return true; /* Віддаємо клієнту Stale значення миттєво */
                }

                pthread_mutex_unlock(&c->locks[h]);
                return true; /* Свіже влучання (Fresh Hit) */
            }
            break; /* Вичерпано Hard TTL */
        }
        curr = curr->next;
    }
    pthread_mutex_unlock(&c->locks[h]);

    /* Синхронний промах (Hard Miss) — блокуюче звернення до джерела */
    bool not_found = false;
    char* fetched = loader_fn(key, &not_found);
    cache_set(c, key, fetched, not_found);

    if (not_found || !fetched) {
        if (fetched) free(fetched);
        return false;
    }

    strncpy(out_val, fetched, out_len - 1);
    out_val[out_len - 1] = '\0';
    free(fetched);
    return true;
}
```
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <shared_mutex>
#include <mutex>
#include <chrono>
#include <random>
#include <optional>
#include <functional>
#include <thread>
#include <memory>

template <typename T>
class ResilientCache {
public:
    struct Entry {
        std::optional<T> value;    // std::nullopt означає Negative Cache (404)
        std::chrono::steady_clock::time_point soft_expiry;
        std::chrono::steady_clock::time_point hard_expiry;
        bool is_refreshing{false};
    };

    struct Options {
        std::chrono::seconds default_ttl{3600};
        std::chrono::seconds negative_ttl{60};
        double soft_ratio{0.75};
        double jitter_ratio{0.15};
    };

    explicit ResilientCache(Options opts = Options{}) : opts_(opts) {}

    // Отримання значення з автоматичним застосуванням Stale-While-Revalidate
    std::optional<T> get_or_load(const std::string& key,
                                 std::function<std::optional<T>()> loader) {
        const auto now = std::chrono::steady_clock::now();

        // 1. Спроба швидкого паралельного читання (Shared Lock)
        {
            std::shared_lock<std::shared_mutex> lock(rw_mutex_);
            auto it = store_.find(key);
            if (it != store_.end() && now < it->second.hard_expiry) {
                // Перевірка необхідності фонового оновлення (Soft TTL)
                if (now >= it->second.soft_expiry && !it->second.is_refreshing) {
                    lock.unlock();
                    try_spawn_async_refresh(key, loader);
                    // Повертаємо поточне значення з кешу (Stale Hit)
                    std::shared_lock<std::shared_mutex> relock(rw_mutex_);
                    auto it_stale = store_.find(key);
                    return (it_stale != store_.end()) ? it_stale->second.value : std::nullopt;
                }
                return it->second.value; // Свіже влучання (Fresh Hit або Negative Hit)
            }
        }

        // 2. Синхронний промах (Hard Miss): блокуючий виклик до бази даних
        return load_and_store_sync(key, loader);
    }

    // Примусова інвалідація ключа при оновленні сутності
    void invalidate(const std::string& key) {
        std::unique_lock<std::shared_mutex> lock(rw_mutex_);
        store_.erase(key);
    }

private:
    std::chrono::seconds compute_jittered_ttl(std::chrono::seconds base) {
        static thread_local std::mt19937 gen(std::random_device{}());
        std::uniform_real_distribution<double> dist(-opts_.jitter_ratio, opts_.jitter_ratio);
        double factor = 1.0 + dist(gen);
        return std::chrono::duration_cast<std::chrono::seconds>(base * factor);
    }

    void try_spawn_async_refresh(const std::string& key,
                                 std::function<std::optional<T>()> loader) {
        std::unique_lock<std::shared_mutex> lock(rw_mutex_);
        auto it = store_.find(key);
        if (it == store_.end() || it->second.is_refreshing) {
            return; // Рейс уже виконується іншим потоком (Single-Flight)
        }
        it->second.is_refreshing = true;

        // Запуск асинхронного фонового оновлення
        std::thread([this, key, loader]() {
            try {
                auto fresh = loader();
                store_value(key, fresh);
            } catch (...) {
                // У разі помилки джерела скидаємо прапорець, залишаючи Stale дані
                std::unique_lock<std::shared_mutex> err_lock(rw_mutex_);
                auto it_err = store_.find(key);
                if (it_err != store_.end()) {
                    it_err->second.is_refreshing = false;
                    // Подовжуємо Soft TTL на 30 секунд для повторної спроби
                    it_err->second.soft_expiry = std::chrono::steady_clock::now() + std::chrono::seconds(30);
                }
            }
        }).detach();
    }

    std::optional<T> load_and_store_sync(const std::string& key,
                                         std::function<std::optional<T>()> loader) {
        auto val = loader();
        store_value(key, val);
        return val;
    }

    void store_value(const std::string& key, const std::optional<T>& val) {
        const auto now = std::chrono::steady_clock::now();
        const bool is_negative = !val.has_value();
        const auto base_ttl = is_negative ? opts_.negative_ttl : opts_.default_ttl;
        const auto actual_ttl = compute_jittered_ttl(base_ttl);

        Entry entry;
        entry.value = val;
        entry.soft_expiry = now + std::chrono::duration_cast<std::chrono::milliseconds>(actual_ttl * opts_.soft_ratio);
        entry.hard_expiry = now + actual_ttl;
        entry.is_refreshing = false;

        std::unique_lock<std::shared_mutex> lock(rw_mutex_);
        store_[key] = std::move(entry);
    }

    Options opts_;
    std::unordered_map<std::string, Entry> store_;
    mutable std::shared_mutex rw_mutex_;
};
```
:::

## 3. Детальний аналіз підводних каменів та механізмів захисту

Розглянемо покроково інженерні деталі та крайові випадки роботи наведеного клієнта:

### Запобігання гонкам даних під час фонової ревалідації
Коли кілька сотень паралельних потоків одночасно звертаються до гарячого ключа, термін `Soft TTL` якого вичерпався, перший потік успішно захоплює ексклюзивне блокування та встановлює прапорець `is_refreshing = true`. Усі інші 999 потоків одразу бачать активний прапорець і негайно повертають закешоване значення (Stale Hit) із субмілісекундною затримкою, не чекаючи на відповідь бази даних. Завдяки цьому реалізується локальний захист від шторму оновлень без блокування робочих потоків вебсервера.

### Стратегія блокувань: шардування проти RWLock
У реалізації на мові C застосовано масив із `HASH_SIZE` незалежних м'ютексів (англ. *striped locks* / *bucket-level locking*). Це усуває взаємне блокування потоків, які працюють з різними ключами кешу, забезпечуючи лінійне масштабування на багатоядерних процесорах. У реалізації на C++ використано `std::shared_mutex`, що дозволяє тисячам потоків одночасно читати гарячі записи через `std::shared_lock` без взаємного очікування, перемикаючись на ексклюзивний `std::unique_lock` лише в мить вставки або оновлення структури.

### Крайовий випадок створення сутності після запису порожнечі
Якщо бот або клієнт запитав профіль користувача з неіснуючим `ID = 501`, клієнт зберігає маркер `std::nullopt` на `negative_ttl = 60` секунд. Якщо через 5 секунд адміністратор реєструє користувача `501`, прикладний сервіс зобов'язаний виконати явний виклик `cache.invalidate("user:501")` під час транзакції створення. Навіть якщо інвалідація не спрацює (наприклад, через збій мережі), короткий час життя порожнього запису гарантує, що максимум за 60 секунд система автоматично зчитає актуальні дані з бази без ручного втручання чергового інженера.

### Стійкість під час аварії первинного сховища (Graceful Degradation)
Якщо база даних перевантажена, повертає таймаути або зазнає аварійного перезапуску під час фонового оновлення, блок обробки помилок перехоплює збій. Замість видалення запису або передачі помилки клієнту, клієнт подовжує `soft_expiry` на 30 секунд і скидає прапорець `is_refreshing = false`. Усі користувачі продовжують миттєво отримувати закешовані дані зі статусом деградації замість системних помилок HTTP 500, дозволяючи команді спокійно відновити працездатність СУБД.

### Контроль виділення пам'яті та лімітування пулу потоків
У високонавантажених системах неконтрольований запуск окремих потоків через `std::thread` або `pthread_create` може вичерпати системні дескриптори ОС (помилка `pthread_create failed: Resource temporarily unavailable`). Для промислового використання запуск асинхронних рейсів делегують фіксованому пулу фонових воркерів (англ. *bounded thread pool*) з обмеженою чергою завдань. Якщо черга пулу заповнена, фоновий рейс просто відкидається, а клієнт продовжує отримувати Stale-дані до наступної спроби.

Крім того, для запобігання переповненню оперативної пам'яті через масоване кешування негативних відповідей (наприклад, під час сканування мільйонів унікальних випадкових рядків) сховище обмежують максимальною кількістю елементів `max_capacity` з політикою витіснення найменш використовуваних записів (LRU або W-TinyLFU). Це гарантує стабільний розмір споживання RAM незалежно від обсягу вхідного зловмисного трафіку.
