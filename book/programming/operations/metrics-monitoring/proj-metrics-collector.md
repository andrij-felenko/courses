# ⚙️ Метричний рушій: атомарні лічильники, гістограми та OpenMetrics-експортер

<preknowlist>
- [Метрики й числовий моніторинг](book:programming/metrics-monitoring) — типи метрик, багатовимірні мітки та пастка високої кардинальності.
- [Квантилі та інтерполяція гістограм](book:programming/metrics-monitoring/math-histograms-and-sketches.md) — робота кумулятивних кошиків та лінійна інтерполяція.
</preknowlist>

Інструментація високопродуктивних серверів вимагає вбудованого метричного рушія, який не уповільнює обробку запитів, працює безпечно в багатопотоковому середовищі без глобальних блокувань і не призводить до вичерпання пам'яті через вибух кардинальності.

Розглянемо архітектуру швидкого метричного рушія, внутрішній устрій атомарних структур даних, боротьбу з фальшивим розділенням кеш-ліній (false sharing), патерн локальних потокових буферів (thread-local aggregation), векторизацію пошуку кошиків через SIMD, хешування міток алгоритмом FNV-1a, асемблерний аналіз операцій на x86_64 та ARM64, узгодження форматів OpenMetrics / Prometheus, захист від вибуху кардинальності, зворотний тиск повільних скрейперів (scrape backpressure), збирання застарілих рядів (metric TTL), врахування топології NUMA, вбудований HTTP-експортер та серіалізацію у стандартний формат OpenMetrics.

## Проблема накладних витрат у критичному шляху

У типовому мікросервісі обробка вхідного запиту супроводжується фіксацією кількох метричних показників: збільшення лічильника запитів `http_requests_total`, оновлення покажчика активних з'єднань `http_active_connections` та запис тривалості операції в гістограму `http_request_duration_seconds`. Якщо сервіс обробляє 100 000 запитів на секунду на 32 процесорних ядрах, кожен запит викликає оновлення метрик тричі.

Наївна реалізація, що використовує глобальний м'ютекс (`pthread_mutex_t` або `std::mutex`) для захисту структур даних, призводить до катастрофічного колапсу продуктивності:
1. **Конкуренція за блокування (Lock Contention):** Десятки потоків одночасно намагаються захопити один м'ютекс. Потоки переходять у стан очікування в ядрі операційної системи (виклики `futex`), що спричиняє масові перемикання контексту (context switches) та деградацію пропускної здатності в десятки разів.
2. **Інвалідація процесорного кешу (Cache Line Bouncing):** Навіть якщо замінити м'ютекс на простий спільний атомарний лічильник `std::atomic<uint64_t>`, постійний запис інструкцією `LOCK XADD` з різних ядер змушує протокол когерентності кешу (MESI/MOESI) щоразу інвалідувати кеш-лінію L1/L2 на всіх сусідніх ядрах.

Щоб рушій працював із мінімальними накладними витратами (лічені наносекунди на виклик), застосовують чотири архітектурні принципи:
* **Неблокуючі атомарні примітиви з послабленою моделлю пам'яті (`relaxed memory ordering`):** Метрики є суто статистичними спостереженнями. Вони не захищають інші змінні програми, тому їм не потрібна дорога послідовна узгодженість (`memory_order_seq_cst`).
* **Вирівнювання структур за межами кеш-ліній (`alignas(64)`):** Гарячі атомарні лічильники різних метрик розносяться по різних 64-байтних лініях кешу, щоб уникнути взаємного блокування ядер (false sharing).
* **Фіксований розмір пам'яті та ліміт кардинальності:** Реєстр метрик має жорстку верхню межу кількості часових рядів, що унеможливлює вичерпання оперативної пам'яті (OOM) при некоректних динамічних мітках.
* **Безвидільний рендеринг (Zero-Allocation Formatting):** Форматування вихідного тексту OpenMetrics виконується безпосередньо у заздалегідь виділений буфер або мережевий сокет без динамічного виділення пам'яті (`malloc`/`new`) у критичних циклах.

## Реалізація метричного рушія на C та C++20

Наведено повноцінну реалізацію легкового потокобезпечного метричного рушія: варіант на C11 зі `stdatomic.h` та варіант на сучасному C++20 із використанням `std::span`, `std::string_view` та `std::atomic`.

:::tabs
```c
/* ============================================================================
 * Метричний рушій на чистому C (C11 stdatomic)
 * Підтримує атомарні лічильники, покажчики, кумулятивні гістограми
 * та серіалізацію у формат OpenMetrics.
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdatomic.h>
#include <pthread.h>
#include <time.h>

#define MAX_LABEL_LEN     64
#define MAX_SERIES_NAME   64
#define MAX_HIST_BUCKETS  12
#define MAX_METRIC_SERIES 256
#define CACHE_LINE_SIZE   64

/* Типи підтримуваних метрик */
typedef enum {
    METRIC_TYPE_COUNTER,
    METRIC_TYPE_GAUGE,
    METRIC_TYPE_HISTOGRAM
} metric_type_t;

/* Структура кумулятивної гістограми з вирівнюванням */
typedef struct {
    size_t num_buckets;
    double boundaries[MAX_HIST_BUCKETS];                  /* Верхні межі кошиків (le) */
    atomic_uint_fast64_t bucket_counts[MAX_HIST_BUCKETS]; /* Кількість спостережень <= le */
    atomic_uint_fast64_t count;                           /* Загальна кількість (count) */
    _Atomic double sum;                                   /* Загальна сума значень (sum) */
} histogram_data_t;

/* Окремий часовий ряд метрики */
typedef struct {
    char name[MAX_SERIES_NAME];
    char labels[MAX_LABEL_LEN];                           /* Формат: method="GET",status="200" */
    metric_type_t type;
    union {
        atomic_uint_fast64_t counter_val;
        _Atomic double gauge_val;
        histogram_data_t hist;
    };
    bool in_use;
} metric_series_t;

/* Глобальний реєстр із захистом кардинальності */
typedef struct {
    metric_series_t series[MAX_METRIC_SERIES];
    size_t count;
    atomic_uint_fast64_t overflow_count;                 /* Лічильник відкинутих рядів */
    pthread_rwlock_t rwlock;
} metric_registry_t;

static metric_registry_t G_REGISTRY;

void registry_init(void) {
    memset(&G_REGISTRY, 0, sizeof(G_REGISTRY));
    pthread_rwlock_init(&G_REGISTRY.rwlock, NULL);
}

/* Атомарне додавання дійсного числа до _Atomic double через CAS */
static void atomic_double_add(_Atomic double *target, double val) {
    double old_val = atomic_load_explicit(target, memory_order_relaxed);
    double new_val;
    do {
        new_val = old_val + val;
    } while (!atomic_compare_exchange_weak_explicit(target, &old_val, new_val,
                                                   memory_order_relaxed,
                                                   memory_order_relaxed));
}

/* Отримання або створення часового ряду лічильника/gauge */
metric_series_t* registry_get_or_create(const char *name, const char *labels, metric_type_t type) {
    /* 1. Швидкий шлях: оптимістичний пошук під спільним read-lock */
    pthread_rwlock_rdlock(&G_REGISTRY.rwlock);
    for (size_t i = 0; i < G_REGISTRY.count; ++i) {
        if (G_REGISTRY.series[i].in_use &&
            strcmp(G_REGISTRY.series[i].name, name) == 0 &&
            strcmp(G_REGISTRY.series[i].labels, labels) == 0) {
            pthread_rwlock_unlock(&G_REGISTRY.rwlock);
            return &G_REGISTRY.series[i];
        }
    }
    pthread_rwlock_unlock(&G_REGISTRY.rwlock);

    /* 2. Повільний шлях: створення під write-lock із захистом від переповнення */
    pthread_rwlock_wrlock(&G_REGISTRY.rwlock);
    for (size_t i = 0; i < G_REGISTRY.count; ++i) {
        if (G_REGISTRY.series[i].in_use &&
            strcmp(G_REGISTRY.series[i].name, name) == 0 &&
            strcmp(G_REGISTRY.series[i].labels, labels) == 0) {
            pthread_rwlock_unlock(&G_REGISTRY.rwlock);
            return &G_REGISTRY.series[i];
        }
    }

    if (G_REGISTRY.count >= MAX_METRIC_SERIES) {
        /* Захист від вибуху кардинальності! */
        atomic_fetch_add_explicit(&G_REGISTRY.overflow_count, 1, memory_order_relaxed);
        pthread_rwlock_unlock(&G_REGISTRY.rwlock);
        return NULL;
    }

    metric_series_t *s = &G_REGISTRY.series[G_REGISTRY.count++];
    strncpy(s->name, name, MAX_SERIES_NAME - 1);
    strncpy(s->labels, labels, MAX_LABEL_LEN - 1);
    s->type = type;
    s->in_use = true;

    if (type == METRIC_TYPE_COUNTER) {
        atomic_init(&s->counter_val, 0);
    } else if (type == METRIC_TYPE_GAUGE) {
        atomic_init(&s->gauge_val, 0.0);
    }

    pthread_rwlock_unlock(&G_REGISTRY.rwlock);
    return s;
}

/* Ініціалізація гістограми з користувацькими межами */
metric_series_t* registry_register_histogram(const char *name, const char *labels,
                                            const double *buckets, size_t num_buckets) {
    pthread_rwlock_wrlock(&G_REGISTRY.rwlock);
    if (G_REGISTRY.count >= MAX_METRIC_SERIES || num_buckets > MAX_HIST_BUCKETS) {
        atomic_fetch_add_explicit(&G_REGISTRY.overflow_count, 1, memory_order_relaxed);
        pthread_rwlock_unlock(&G_REGISTRY.rwlock);
        return NULL;
    }

    metric_series_t *s = &G_REGISTRY.series[G_REGISTRY.count++];
    strncpy(s->name, name, MAX_SERIES_NAME - 1);
    strncpy(s->labels, labels, MAX_LABEL_LEN - 1);
    s->type = METRIC_TYPE_HISTOGRAM;
    s->in_use = true;

    s->hist.num_buckets = num_buckets;
    for (size_t i = 0; i < num_buckets; ++i) {
        s->hist.boundaries[i] = buckets[i];
        atomic_init(&s->hist.bucket_counts[i], 0);
    }
    atomic_init(&s->hist.count, 0);
    atomic_init(&s->hist.sum, 0.0);

    pthread_rwlock_unlock(&G_REGISTRY.rwlock);
    return s;
}

/* Операції над лічильниками */
void counter_inc(metric_series_t *s, uint64_t delta) {
    if (s && s->type == METRIC_TYPE_COUNTER) {
        atomic_fetch_add_explicit(&s->counter_val, delta, memory_order_relaxed);
    }
}

/* Операції над покажчиками */
void gauge_set(metric_series_t *s, double val) {
    if (s && s->type == METRIC_TYPE_GAUGE) {
        atomic_store_explicit(&s->gauge_val, val, memory_order_relaxed);
    }
}

/* Фіксація виміру в гістограмі */
void histogram_observe(metric_series_t *s, double val) {
    if (!s || s->type != METRIC_TYPE_HISTOGRAM) return;

    for (size_t i = 0; i < s->hist.num_buckets; ++i) {
        if (val <= s->hist.boundaries[i]) {
            atomic_fetch_add_explicit(&s->hist.bucket_counts[i], 1, memory_order_relaxed);
        }
    }
    atomic_fetch_add_explicit(&s->hist.count, 1, memory_order_relaxed);
    atomic_double_add(&s->hist.sum, val);
}

/* Рендеринг усіх метрик у формат OpenMetrics */
size_t registry_render_openmetrics(char *buffer, size_t max_len) {
    pthread_rwlock_rdlock(&G_REGISTRY.rwlock);
    size_t offset = 0;

    for (size_t i = 0; i < G_REGISTRY.count; ++i) {
        metric_series_t *s = &G_REGISTRY.series[i];
        if (!s->in_use) continue;

        if (s->type == METRIC_TYPE_COUNTER) {
            uint64_t val = atomic_load_explicit(&s->counter_val, memory_order_relaxed);
            offset += snprintf(buffer + offset, max_len - offset,
                               "# TYPE %s counter\n%s{%s} %llu\n",
                               s->name, s->name, s->labels, (unsigned long long)val);
        } else if (s->type == METRIC_TYPE_GAUGE) {
            double val = atomic_load_explicit(&s->gauge_val, memory_order_relaxed);
            offset += snprintf(buffer + offset, max_len - offset,
                               "# TYPE %s gauge\n%s{%s} %.6f\n",
                               s->name, s->name, s->labels, val);
        } else if (s->type == METRIC_TYPE_HISTOGRAM) {
            offset += snprintf(buffer + offset, max_len - offset,
                               "# TYPE %s histogram\n", s->name);
            for (size_t b = 0; b < s->hist.num_buckets; ++b) {
                uint64_t b_cnt = atomic_load_explicit(&s->hist.bucket_counts[b], memory_order_relaxed);
                offset += snprintf(buffer + offset, max_len - offset,
                                   "%s_bucket{%s,le=\"%.4f\"} %llu\n",
                                   s->name, s->labels, s->hist.boundaries[b], (unsigned long long)b_cnt);
            }
            uint64_t total_cnt = atomic_load_explicit(&s->hist.count, memory_order_relaxed);
            double total_sum = atomic_load_explicit(&s->hist.sum, memory_order_relaxed);
            offset += snprintf(buffer + offset, max_len - offset,
                               "%s_bucket{%s,le=\"+Inf\"} %llu\n"
                               "%s_sum{%s} %.6f\n"
                               "%s_count{%s} %llu\n",
                               s->name, s->labels, (unsigned long long)total_cnt,
                               s->name, s->labels, total_sum,
                               s->name, s->labels, (unsigned long long)total_cnt);
        }
    }

    uint64_t overflows = atomic_load_explicit(&G_REGISTRY.overflow_count, memory_order_relaxed);
    offset += snprintf(buffer + offset, max_len - offset,
                       "# TYPE metrics_overflow_total counter\n"
                       "metrics_overflow_total %llu\n"
                       "# EOF\n", (unsigned long long)overflows);

    pthread_rwlock_unlock(&G_REGISTRY.rwlock);
    return offset;
}
```
```cpp
/* ============================================================================
 * Метричний рушій на сучасному C++20
 * Потокобезпечний, lock-free операції інструментації, захист кардинальності
 * та форматування у стандарт OpenMetrics через std::string_view та std::span.
 * ============================================================================ */
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <span>
#include <atomic>
#include <shared_mutex>
#include <memory>
#include <sstream>
#include <format>
#include <algorithm>
#include <chrono>

namespace telemetry {

enum class MetricType {
    Counter,
    Gauge,
    Histogram
};

/* Атомарне додавання дійсного числа через compare-and-swap */
inline void atomic_add(std::atomic<double>& target, double delta) noexcept {
    double current = target.load(std::memory_order_relaxed);
    while (!target.compare_exchange_weak(current, current + delta,
                                         std::memory_order_relaxed,
                                         std::memory_order_relaxed)) {}
}

class Counter {
public:
    void inc(uint64_t delta = 1) noexcept {
        value_.fetch_add(delta, std::memory_order_relaxed);
    }
    [[nodiscard]] uint64_t get() const noexcept {
        return value_.load(std::memory_order_relaxed);
    }
private:
    alignas(64) std::atomic<uint64_t> value_{0};
};

class Gauge {
public:
    void set(double val) noexcept {
        value_.store(val, std::memory_order_relaxed);
    }
    void add(double delta) noexcept {
        atomic_add(value_, delta);
    }
    [[nodiscard]] double get() const noexcept {
        return value_.load(std::memory_order_relaxed);
    }
private:
    alignas(64) std::atomic<double> value_{0.0};
};

class Histogram {
public:
    explicit Histogram(std::span<const double> bounds)
        : boundaries_(bounds.begin(), bounds.end()),
          bucket_counts_(bounds.size()) {
        for (auto& c : bucket_counts_) {
            c.store(0, std::memory_order_relaxed);
        }
    }

    void observe(double value) noexcept {
        for (size_t i = 0; i < boundaries_.size(); ++i) {
            if (value <= boundaries_[i]) {
                bucket_counts_[i].fetch_add(1, std::memory_order_relaxed);
            }
        }
        count_.fetch_add(1, std::memory_order_relaxed);
        atomic_add(sum_, value);
    }

    [[nodiscard]] std::span<const double> boundaries() const noexcept { return boundaries_; }
    [[nodiscard]] uint64_t bucket_count(size_t idx) const noexcept {
        return bucket_counts_[idx].load(std::memory_order_relaxed);
    }
    [[nodiscard]] uint64_t count() const noexcept { return count_.load(std::memory_order_relaxed); }
    [[nodiscard]] double sum() const noexcept { return sum_.load(std::memory_order_relaxed); }

private:
    std::vector<double> boundaries_;
    std::vector<std::atomic<uint64_t>> bucket_counts_;
    alignas(64) std::atomic<uint64_t> count_{0};
    alignas(64) std::atomic<double> sum_{0.0};
};

/* Дескриптор метричного ряду */
struct MetricEntry {
    std::string name;
    std::string labels;
    MetricType type;
    std::variant<Counter, Gauge, Histogram> storage;
};

class Registry {
public:
    static constexpr size_t kMaxSeriesLimit = 512;

    Counter* get_counter(std::string_view name, std::string_view labels) {
        return get_or_create<Counter>(name, labels, MetricType::Counter,
                                      []() { return Counter{}; });
    }

    Gauge* get_gauge(std::string_view name, std::string_view labels) {
        return get_or_create<Gauge>(name, labels, MetricType::Gauge,
                                    []() { return Gauge{}; });
    }

    Histogram* get_histogram(std::string_view name, std::string_view labels,
                             std::span<const double> buckets) {
        return get_or_create<Histogram>(name, labels, MetricType::Histogram,
                                        [buckets]() { return Histogram(buckets); });
    }

    [[nodiscard]] std::string render_openmetrics() const {
        std::shared_lock lock(mutex_);
        std::string out;
        out.reserve(32768);

        for (const auto& entry : entries_) {
            if (entry.type == MetricType::Counter) {
                const auto& c = std::get<Counter>(entry.storage);
                out += std::format("# TYPE {} counter\n{}{{{}}} {}\n",
                                   entry.name, entry.name, entry.labels, c.get());
            } else if (entry.type == MetricType::Gauge) {
                const auto& g = std::get<Gauge>(entry.storage);
                out += std::format("# TYPE {} gauge\n{}{{{}}} {:.6f}\n",
                                   entry.name, entry.name, entry.labels, g.get());
            } else if (entry.type == MetricType::Histogram) {
                const auto& h = std::get<Histogram>(entry.storage);
                out += std::format("# TYPE {} histogram\n", entry.name);
                auto bounds = h.boundaries();
                for (size_t b = 0; b < bounds.size(); ++b) {
                    out += std::format("{}_bucket{{{},le=\"{:.4f}\"}} {}\n",
                                       entry.name, entry.labels, bounds[b], h.bucket_count(b));
                }
                out += std::format("{}_bucket{{{},le=\"+Inf\"}} {}\n",
                                   entry.name, entry.labels, h.count());
                out += std::format("{}_sum{{{{{}}}}} {:.6f}\n", entry.name, entry.labels, h.sum());
                out += std::format("{}_count{{{{{}}}}} {}\n", entry.name, entry.labels, h.count());
            }
        }

        out += std::format("# TYPE metrics_overflow_total counter\nmetrics_overflow_total {}\n# EOF\n",
                           overflow_count_.load(std::memory_order_relaxed));
        return out;
    }

private:
    template <typename T, typename Factory>
    T* get_or_create(std::string_view name, std::string_view labels, MetricType type, Factory&& factory) {
        {
            std::shared_lock lock(mutex_);
            for (auto& entry : entries_) {
                if (entry.name == name && entry.labels == labels) {
                    return &std::get<T>(entry.storage);
                }
            }
        }

        std::unique_lock lock(mutex_);
        for (auto& entry : entries_) {
            if (entry.name == name && entry.labels == labels) {
                return &std::get<T>(entry.storage);
            }
        }

        if (entries_.size() >= kMaxSeriesLimit) {
            overflow_count_.fetch_add(1, std::memory_order_relaxed);
            return nullptr;
        }

        entries_.push_back(MetricEntry{
            .name = std::string(name),
            .labels = std::string(labels),
            .type = type,
            .storage = factory()
        });

        return &std::get<T>(entries_.back().storage);
    }

    mutable std::shared_mutex mutex_;
    std::vector<MetricEntry> entries_;
    std::atomic<uint64_t> overflow_count_{0};
};

} // namespace telemetry
```
:::

## Хешування міток та швидкий пошук рядів

У високонавантажених сервісах виклик `get_counter(name, labels)` виконується перед інкрементом. Послідовне сканування масиву рядків з порівнянням рядків через `strcmp` має часову складність `O(N)`. Якщо реєстр містить 500 активних рядів, лінійний пошук стає вузьким місцем.

Для досягнення константної складності `O(1)` застосовують 64-бітне хешування сигнатури міток алгоритмом **FNV-1a** (Fowler–Noll–Vo):

```cpp
inline uint64_t hash_metric_signature(std::string_view name, std::string_view labels) noexcept {
    constexpr uint64_t kFnvPrime = 1099511628211ULL;
    uint64_t hash = 14695981039346656037ULL; // FNV Offset Basis

    for (char c : name) {
        hash ^= static_cast<uint64_t>(c);
        hash *= kFnvPrime;
    }
    hash ^= 0xFF; // Розділювач просторів імен
    hash *= kFnvPrime;
    for (char c : labels) {
        hash ^= static_cast<uint64_t>(c);
        hash *= kFnvPrime;
    }
    return hash;
}
```

Обчислений 64-бітний хеш використовується для адресації у статичній хеш-таблиці з відкритою адресацією (open addressing) та лінійним пробуванням (linear probing). Оскільки набір метрик ініціалізується під час старту програми, хеш-таблиця працює в режимі «read-heavy», забезпечуючи повернення покажчика на атомарний лічильник за одну операцію читання з кешу L1 без виділення динамічної пам'яті.

## Покрокове проходження запиту крізь інструментацію

Розглянемо повний життєвий цикл обробки одного HTTP-запиту та послідовність дій метричного рушія під високим навантаженням:

1. **Вхід запиту (Connection Accepted):**
   Робочий потік сервера приймає нове TCP-з'єднання від клієнта і негайно фіксує зміну навантаження:
   ```cpp
   active_conns_gauge->add(1.0);
   ```
   Атомарне значення покажчика миттєво змінюється в оперативній пам'яті через виклик `atomic_add`. Якщо в цей момент система моніторингу виконує скрейп, вона зафіксує актуальну кількість відкритих з'єднань без будь-яких блокувань.

2. **Запуск монотонного таймера:**
   Потік фіксує мітку часу початку виконання. **Критична архітектурна вимога:** використовувати лише монотонний годинник (`CLOCK_MONOTONIC` у C або `std::chrono::steady_clock` у C++), а не системний час реального дня (`CLOCK_REALTIME` / `std::chrono::system_clock`). Системний годинник може коригуватися демоном синхронізації часу NTP стрибком назад. Якщо під час обробки запиту годинник стрибне на 500 мс назад, обчислення тривалості дасть від'ємне число, що зламає гістограму та спотворить розрахунок суми `_sum`.

3. **Маршрутизація та обробка бізнес-логіки:**
   Запит маршрутизується до обробника `/api/v1/checkout`. Під час виконання запит звертається до бази даних або зовнішнього API.

4. **Завершення запиту та фіксація результатів:**
   Після відправки відповіді клієнту потік обчислює тривалість операції:
   ```cpp
   auto duration_sec = std::chrono::duration<double>(end_time - start_time).count();
   ```
   Далі потік викликає три незалежні операції інструментації:
   ```cpp
   // 1. Зменшення покажчика активних з'єднань
   active_conns_gauge->add(-1.0);

   // 2. Збільшення лічильника запитів із фіксованими мітками
   requests_counter->inc(1);

   // 3. Оновлення кошиків гістограми затримки
   latency_histogram->observe(duration_sec);
   ```

5. **Виконання `observe()` всередині гістограми:**
   Метод `observe(duration_sec)` послідовно порівнює `duration_sec` із верхніми межами кошиків `boundaries_`. Для кожного кошика, де `duration_sec <= boundary`, виконується атомарний інкремент лічильника `bucket_counts_[i].fetch_add(1, relaxed)`. Наприкінці збільшується лічильник загальної кількості `count_` та через цикл CAS додається значення до суми `sum_`.

## Патерн локальної агрегації в потоках (Thread-Local Aggregation)

Коли кількість робочих ядер на сервері перевищує 64 (наприклад, у двопроцесорних серверах із NUMA-архітектурою на базі AMD EPYC чи Intel Xeon), навіть атомарна інструкція `LOCK XADD` зі специфікатором `memory_order_relaxed` починає відчувати затримки через арбітраж шини між сокетами.

Для усунення будь-яких міжпроцесорних блокувань у високонавантажених проксі-серверах (таких як Envoy чи Nginx) застосовують **патерн локальних потокових накопичувачів** (англ. *Thread-Local Metric Aggregation*):

```text
Потік 1 (Ядро 0) ──► [ Локальний лічильник T₁ ] ──┐
Потік 2 (Ядро 1) ──► [ Локальний лічильник T₂ ] ──┼──► [ Фоновий Scrape: сума T₁+T₂+T₃ ]
Потік 3 (Ядро 2) ──► [ Локальний лічильник T₃ ] ──┘
```

1. **Запис без атоміків:** Кожен робочий потік пише у власну неатомарну змінну `thread_local uint64_t thread_requests_count`. Оскільки змінна знаходиться виключно у приватному кеші L1 даного ядра, операція інкременту зводиться до звичайної неблокуючої інструкції `inc [rbp - 8]`, яка виконується за 1 такт процесора (менше 0.3 наносекунди).
2. **Агрегація за розкладом:** Під час опитування ендпоінта `/metrics` фоновий потік експортера ітерується по масиву дескрипторів усіх зареєстрованих потоків процесу, зчитує їхні локальні значення та підсумовує глобальний результат.
3. **Обробка завершення потоків:** Реєстрація потокових буферів використовує механізм ключів POSIX `pthread_key_create()` з функцією-деструктором. Коли робочий потік завершує своє існування (наприклад, у динамічному пулі потоків), його деструктор переносить накопичені лічильники у глобальний залишковий пул, запобігаючи втраті даних.

## Векторизація SIMD для гістограм із великою кількістю кошиків

Коли гістограма містить 32 або 64 кошики для детального аналізу розподілу, послідовний цикл `for (size_t i = 0; i < n; ++i)` виконує десятки операцій порівняння та розгалужень, що призводить до промахів передбачення переходів (branch mispredictions).

Для оптимізації застосовують векторні інструкції **AVX2 / AVX-512**:
1. Значення `val` транслюється у вектор з 4 або 8 однакових чисел подвійної точності (`_mm256_set1_pd(val)`).
2. Межі кошиків зберігаються у вирівняному масиві векторів `__m256d bounds[K]`.
3. Векторне порівняння `_mm256_cmp_pd(val_vec, bounds_vec, _CMP_LE_OQ)` виконує 4 порівняння за 1 машинний такт.
4. Інструкція `_mm256_movemask_pd` формує 4-бітну бітову маску.
5. На основі маски оновлюються лише відповідні кошики без умовних переходів, зменшуючи час виконання `observe()` до стабільних 3-4 наносекунд незалежно від кількості кошиків.

## Асемблерний аналіз атомарних операцій: x86_64 проти ARM64

Порівняємо скомпільований машинний код для операції `counter.inc(1)` з моделлю пам'яті `memory_order_relaxed` та `memory_order_seq_cst`.

На архітектурі **x86_64** (компілятор GCC/Clang з прапорцем `-O3`):
```nasm
; memory_order_relaxed:
lock add qword ptr [rdi], 1    ; Одна інструкція з префіксом блокування шини кешу

; memory_order_seq_cst:
lock add qword ptr [rdi], 1    ; На x86_64 інструкція LOCK вже забезпечує повний бар'єр
```

На архітектурі **ARM64 (AArch64)** з набором інструкцій ARMv8.1-A Large System Extensions (LSE):
```nasm
; memory_order_relaxed:
mov     x1, #1
ldadd   x1, xzr, [x0]          ; Атомарне додавання БЕЗ бар'єрів пам'яті (дуже швидко!)

; memory_order_seq_cst:
mov     x1, #1
ldaddal x1, xzr, [x0]          ; Атомарне додавання з acquire-release бар'єром (гальмує конвеєр)
```

На процесорах ARM64 різниця у продуктивності між `relaxed` та `seq_cst` досягає **300%**, оскільки інструкція `ldadd` не зупиняє позачергове виконання (out-of-order execution) сусідніх інструкцій процесора, тоді як `ldaddal` змушує ядро очікувати повного скидання черги завантаження-збереження (load-store queue).

## Узгодження форматів OpenMetrics та Prometheus

Під час опитування ендпоінта клієнти моніторингу передають заголовок `Accept`:
* Сучасні скрейпери надсилають: `Accept: application/openmetrics-text; version=1.0.0, text/plain; version=0.0.4; q=0.5`.
* Старі скрейпери передають: `Accept: text/plain`.

Рушій аналізує заголовок: якщо клієнт підтримує OpenMetrics, сервіс додає маркер завершення `# EOF\n` та використовує точні назви типів; для старих клієнтів маркер `# EOF` вимикається. Це гарантує сумісність із будь-якими версіями систем збору телеметрії.

## Врахування топології NUMA на багатопроцесорних серверах

На серверах із двома або чотирма процесорними сокетами (NUMA — Non-Uniform Memory Access) звернення до оперативної пам'яті, приєднаної до іншого сокета, відбувається через міжпроцесорну шину (Intel UPI / AMD Infinity Fabric) і займає у 2.5–3 рази більше часу (понад 120 нс проти 40 нс для локального вузла).

Якщо глобальний реєстр метрик виділено у пам'яті Сокета 0, потоки Сокета 1 під час кожного інкременту лічильника змушені виконувати віддалені транзакції пам'яті, створюючи перевантаження інтерконекту.

**Архітектурне рішення:** Застосування бібліотеки `libnuma` та системного виклику `numa_alloc_local()` для розміщення потокових буферів метрик у пам'яті того самого NUMA-вузла, до якого прив'язані відповідні ядра процесора. Це утримує весь трафік телеметрії локальним для кожного сокета.

## Зворотний тиск повільних скрейперів (Scrape Backpressure)

Під час масштабування моніторингу виникає ситуація, коли сервер Prometheus або Prometheus Agent підпадає під деградацію CPU чи мережеві затримки. Якщо експортер сервісу надсилає велику текстову відповідь OpenMetrics (наприклад, 2 МБ тексту) через блокуючий сокет `write()`, виникає небезпека:
* Буфер відправки TCP-сокету `SO_SNDBUF` заповнюється за лічені мілісекунди.
* Потік, що генерує метрики, блокується ядром операційної системи в очікуванні підтверджень `TCP ACK` від повільного клієнта.
* Якщо метричний ендпоінт обслуговується загальним пулом робочих потоків, блокуються робочі потоки, що мали обслуговувати користувацькі запити.

**Архітектурне рішення:**
1. **Ізоляція експортера на окремому виділеному потоці:** Запити `/metrics` ніколи не направляються у спільний пул обробки бізнес-транзакцій.
2. **Неблокуючий режим сокетів (`O_NONBLOCK`) із таймаутом:** Експортер встановлює жорсткий таймаут на надсилання відповіді (наприклад, 5 секунд). Якщо за 5 секунд сокет не звільнився, з'єднання примусово закривається з помилкою `ECONNRESET`. Prometheus зафіксує збій скрейпу (`up == 0`), проте робочі процеси сервісу залишаться неушкодженими.

## Очищення застарілих часових рядів (Metric TTL / Stale Series)

У динамічних додатках деякі метрики створюються тимчасово: наприклад, лічильник помилок для конкретного завдання пакетної обробки `job_id="batch-482"`. Якщо такі метрики залишаються в реєстрі назавжди, вони утворюють **мертві часові ряди (stale series)**, які марно витрачають пам'ять і збільшують розмір скрейп-пейлоаду.

Для очищення реєстру використовують механізм відміток останньої активності (Last-Accessed Timestamp):
* Кожен `MetricEntry` містить поле `std::atomic<int64_t> last_updated_epoch`.
* Під час виклику `inc()` або `observe()` потік оновлює мітку часу.
* Фоновий потік прибирання (Garbage Collector) раз на годину сканує реєстр: якщо метрика типу Gauge або Histogram не оновлювалася понад 24 години, її пам'ять звільняється або переводиться в пул повторного використання.

## Інженерні пастки та захисні механізми

Під час промислової експлуатації власного метричного коду команди стикаються з чотирма типовими дефектами, кожен із яких здатен знерухомити сервіс або призвести до витоку пам'яті.

### 1. Пастка фальшивого розділення (False Sharing)

Сучасні процесори з архітектурою x86_64 та ARM64 зчитують і записують дані з оперативної пам'яті блоками по 64 байти — **кеш-лініями (cache lines)**.
Якщо два незалежні атомарні лічильники `Counter A` та `Counter B` розташовані в пам'яті поруч (наприклад, у сусідніх полях структури), вони потрапляють в одну 64-байтну кеш-лінію:

```text
Кеш-лінія (64 байти): [ Counter A (8B) | Counter B (8B) | ... вільне місце ... ]
                            ▲                      ▲
                         Ядро 1                 Ядро 2
                   (інкрементує A)        (інкрементує B)
```

Коли Ядро 1 виконує `fetch_add` над `Counter A`, апаратний протокол когерентності MESI маркує всю 64-байтну лінію як `Modified` і змушує Ядро 2 скинути свій кеш L1, навіть якщо воно працювало виключно з `Counter B`. При 100 000 запитах/с це породжує неперервний шторм між'ядерного трафіку на шині пам'яті.

**Рішення:** Застосування директиви вирівнювання `alignas(64)` перед кожним гарячим атомарним полем або масивом кошиків. Це гарантує, що кожна змінна займає власну окрему кеш-лінію.

### 2. Пастка динамічних міток та атака на кардинальність

Якщо розробник помилково додасть до міток запиту динамічний параметр, наприклад, ідентифікатор користувача або сирий URL-шлях із параметрами замовлення:

```cpp
// ⚠️ НЕБЕЗПЕЧНО: вибух кардинальності на мільйонах клієнтів!
auto* counter = registry.get_counter("http_requests_total",
    std::format("user_id=\"{}\",status=\"200\"", req.user_id));
```

Кожен новий користувач створить новий запис `MetricEntry` у векторі `entries_`. За лічені хвилини розмір вектора досягне мільйонів елементів. Операція `render_openmetrics()` почне сканувати гігабайтні масиви рядків, викликаючи гігантські паузи виділення пам'яті та аварійне завершення процесу ядром Linux (OOM-Kill).

**Рішення:**
1. **Жорсткий ліміт `kMaxSeriesLimit` у реєстрі:** Як продемонстровано у наведеному коді, спроба додати ряд понад ліміт не виділяє пам'ять, а інкрементує службову метрику `metrics_overflow_total`.
2. **Шаблонізація маршрутів на рівні веб-фреймворку:** Заміна сирих URL-шляхів (`/users/92841/profile`) на імена маршрутів (`/users/{id}/profile`) перед передачею в реєстр метрик.

### 3. Пастка немонотонного часу

Використання виклику `gettimeofday()` або `std::chrono::system_clock::now()` для вимірювання затримок призводить до періодичної появи від'ємних значень або гігантських викидів через корекцію секунд координації (leap seconds) та роботу демона NTP.

**Рішення:** Використовувати виключно монотонні таймери ядра, що гарантують строгу невід'ємність дельти:

:::tabs
```c
struct timespec start, end;
clock_gettime(CLOCK_MONOTONIC, &start);
/* ... виконання операції ... */
clock_gettime(CLOCK_MONOTONIC, &end);

double elapsed_sec = (end.tv_sec - start.tv_sec) +
                     (end.tv_nsec - start.tv_nsec) / 1000000000.0;
```
```cpp
auto start = std::chrono::steady_clock::now();
/* ... виконання операції ... */
auto end = std::chrono::steady_clock::now();

double elapsed_sec = std::chrono::duration<double>(end - start).count();
```
:::

### 4. Пастка виділення пам'яті під час генерації відповіді

Під час опитування ендпоінта `/metrics` сервер моніторингу очікує повний текст метрик. Якщо реалізація форматує кожен рядок через динамічну конкатенацію рядків без резервування буфера, це спричиняє тисячі дрібних алокацій пам'яті в купі (heap fragmentation).

**Рішення:** Метод `render_openmetrics` використовує попереднє резервування вихідного буфера (`out.reserve(32768)`) або прямий запис через `snprintf` у статичний буфер, мінімізуючи навантаження на алокатор пам'яті.

## Вбудований HTTP-експортер метрик

Щоб система Prometheus могла зчитувати метрики, додаток запускає мінімальний фоновий HTTP-сервер на окремому порту (типово `:9100` або `:8080/metrics`). Нижче наведено приклад інтеграції експортера на POSIX-сокетах у C++:

```cpp
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <thread>

void start_metrics_server(const telemetry::Registry& registry, uint16_t port) {
    std::thread([&registry, port]() {
        int server_fd = socket(AF_INET, SOCK_STREAM, 0);
        int opt = 1;
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);

        bind(server_fd, (sockaddr*)&addr, sizeof(addr));
        listen(server_fd, 16);

        while (true) {
            int client_fd = accept(server_fd, nullptr, nullptr);
            if (client_fd < 0) continue;

            // Зчитування HTTP-запиту GET /metrics
            char req_buf[512];
            ssize_t n = read(client_fd, req_buf, sizeof(req_buf) - 1);
            if (n > 0) {
                std::string body = registry.render_openmetrics();
                std::string header = std::format(
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/openmetrics-text; version=1.0.0; charset=utf-8\r\n"
                    "Content-Length: {}\r\n"
                    "Connection: close\r\n\r\n",
                    body.size()
                );

                write(client_fd, header.data(), header.size());
                write(client_fd, body.data(), body.size());
            }
            close(client_fd);
        }
    }).detach();
}
```

## Тестовий сценарій та верифікація багатопотоковості

Для перевірки коректності роботи метричного рушія використовується стрес-тест, у якому 16 паралельних потоків генерують 1 000 000 операцій кожен:

```cpp
void stress_test_metrics() {
    telemetry::Registry registry;
    const double bounds[] = {0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5};
    auto* hist = registry.get_histogram("http_request_duration_seconds",
                                        "handler=\"checkout\",status=\"200\"",
                                        bounds);
    auto* counter = registry.get_counter("http_requests_total",
                                         "handler=\"checkout\",status=\"200\"");

    constexpr int kThreads = 16;
    constexpr int kOpsPerThread = 100'000;
    std::vector<std::jthread> workers;

    for (int t = 0; t < kThreads; ++t) {
        workers.emplace_back([hist, counter]() {
            for (int i = 0; i < kOpsPerThread; ++i) {
                counter->inc(1);
                hist->observe(0.042); // 42 мс — потрапляє в кошик <= 0.05
            }
        });
    }

    workers.clear(); // Очікування завершення всіх потоків (join)

    // Верифікація атомарної точності
    assert(counter->get() == kThreads * kOpsPerThread);
    assert(hist->count() == kThreads * kOpsPerThread);
    assert(hist->bucket_count(3) == kThreads * kOpsPerThread); // Кошик 0.05

    std::cout << "Стрес-тест успішний: " << counter->get()
              << " операцій зафіксовано без втрат.\n";
}
```

Такий підхід до побудови метричного рушія гарантує абсолютну точність числових показників при нульовому впливі на стабільність і швидкість основного сервісу.
