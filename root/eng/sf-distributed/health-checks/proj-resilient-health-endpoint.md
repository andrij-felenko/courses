# ⚙️ Реалізація стійкого модуля перевірки працездатності: багаторівневий health-check, кешування статусу та захист від каскадних рестартів

У високонавантажених мікросервісних архітектурах наївна реалізація ендпоінтів перевірки працездатності стає причиною важких системних аварій. Якщо балансувальники навантаження, хмарний оркестратор та системи моніторингу одночасно надсилають десятки перевірок на секунду, а обробник `/healthz` під час кожного виклику виконує синхронні блокуючі запити або важкі системні виклики, сервіс створює штучну відмову в обслуговуванні (Self-Inflicted DoS) сам для себе.

Розгляньмо інженерні проблеми наївних реалізацій та збудуймо виробничий модуль перевірки працездатності з захистом від каскадних збоїв.

## Чому наївний health-check руйнує продакшн

Типова помилка початківців полягає у створенні простого маршруту HTTP, який у тілі обробника викликає метод `db.ping()` або сканує системні ресурси. У реальній експлуатації такий підхід спричиняє три критичні дефекти:

### 1. Голодування пулу потоків (Thread Starvation)
Якщо застосунок обслуговує клієнтські запити та перевірки здоров'я в єдиному пулі робочих потоків (Worker Pool), під час пікового навантаження всі потоки виявляються зайнятими обробкою користувачів. Черговий HTTP-запит від балансувальника потрапляє в чергу очікування сокета. 

Балансувальник не отримує відповіді за встановлений таймаут (наприклад, 1 секунда) і позначає абсолютно здоровий, але завантажений вузол як `Unhealthy`, відключаючи його від трафіку. Навантаження на решту серверів зростає, спричиняючи лавиноподібне падіння всього кластера.

### 2. Шторм повторних перевірок на спільній базі даних
Якщо 200 екземплярів мікросервісу кожні 2 секунди пінгують центральну базу даних усередині ендпоінта перевірки, база отримує постійний фоновий потік із 100 запитів на секунду. Коли навантаження на СУБД зростає через важкий користувацький звіт, затримка виконання запиту `SELECT 1` збільшується з 1 мілісекунди до 2 секунд. 

Усі 200 екземплярів одночасно фіксують таймаут перевірки здоров'я, оркестратор вбиває всі 200 процесів і запускає їх заново. Під час рестарту нові процеси одночасно відкривають пули з'єднань до вже перевантаженої СУБД (ефект гримучої отари — Thundering Herd), остаточно знищуючи базу даних.

### 3. Миготіння статусу (Flapping)
Через короткочасні сплески затримок у віртуальній мережі поодинокі пакети перевірки можуть губитися. Без фільтрації гістерезису статус екземпляра починає щосекунди перемикатися між `Healthy` та `Unhealthy`. Це викликає безперервні перебудови таблиць маршрутизації в балансувальниках (iptables / IPVS / eBPF rules update), що призводить до сплесків споживання процесорного часу ядра операційної системи.

## Архітектура стійкого модуля моніторингу

Щоб усунути ці загрози, надійний модуль моніторингу будується на базі чотирьох архітектурних механізмів:

```
[Запит перевірки /healthz]
         │
         ▼
 ┌───────────────────────────────┐
 │ 1. Перевірка свіжості кешу    │──(TTL < 2000 мс)──> [Миттєве повернення кешу]
 └───────────────────────────────┘
         │ (Кеш застарів)
         ▼
 ┌───────────────────────────────┐
 │ 2. Роздільна оцінка метрик   │
 │   • Liveness: CPU/Heap RAM    │
 │   • Readiness: DB / Conns /   │
 │     Atomic Drain Flag         │
 └───────────────────────────────┘
         │
         ▼
 ┌───────────────────────────────┐
 │ 3. Фільтр гістерезису         │
 │   • FailureThreshold (k=3)    │
 │   • SuccessThreshold (m=2)    │
 └───────────────────────────────┘
         │
         ▼
 ┌───────────────────────────────┐
 │ 4. Оновлення кешу та вивід   │──> [HTTP 200 / 503 JSON]
 └───────────────────────────────┘
```

1. **Суворе розмежування Liveness та Readiness:**
   * **Liveness:** перевіряє виключно локальний стан процесу в оперативній пам'яті (чи не заблокований цикл подій, чи не вичерпано локальний ліміт пам'яті процесу). Вона ніколи не робить мережевих викликів до зовнішніх систем.
   * **Readiness:** оцінює готовність обслуговувати трафік (стан локального пулу з'єднань, стан прогріву кешу, відсутність сигналу завершення роботи).
2. **Кешування результатів оцінки (Debouncing / TTL Caching):**
   * Оцінка стану виконується не частіше одного разу на фіксований квант часу (наприклад, `CACHE_TTL_MS = 2000`).
   * Будь-яка кількість паралельних запитів перевірки від зовнішніх систем моніторингу миттєво отримує з пам'яті кешований зліпок без повторних обчислень та блокувань.
3. **Гістерезисний автомат станів (Hysteresis State Machine):**
   * Перехід зі стану `Healthy` у стан `Unhealthy` вимагає `k` послідовних збоїв (наприклад, 3 збої поспіль).
   * Повернення зі стану `Unhealthy` у стан `Healthy` вимагає `m` послідовних успіхів (наприклад, 2 успішні перевірки поспіль).
4. **Атомарна координація граційного вимкнення (Graceful Drain):**
   * Обробник сигналу ОС `SIGTERM` атомарно встановлює прапорець `is_draining = true` та інвалідує кеш готовності.
   * Наступний запит readiness негайно повертає код `503 Service Unavailable`, що змушує балансувальник зняти трафік з екземпляра до фізичної зупинки процесу.

## Реалізація стійкого модуля моніторингу

Нижче наведено повну реалізацію такого виробничого модуля мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define CACHE_TTL_MS 2000
#define FAILURE_THRESHOLD 3
#define SUCCESS_THRESHOLD 2

/* Можливі стани працездатності */
typedef enum {
    HEALTH_STATUS_HEALTHY = 0,
    HEALTH_STATUS_DEGRADED = 1,
    HEALTH_STATUS_UNHEALTHY = 2
} HealthStatus;

/* Структура діагностичного звіту */
typedef struct {
    HealthStatus status;
    int http_code;
    uint64_t evaluated_at_ms;
    char details[256];
} HealthReport;

/* Внутрішній стан модуля перевірки */
typedef struct {
    /* Метрики локального процесу */
    size_t memory_used_mb;
    size_t memory_limit_mb;
    int active_workers;
    int max_workers;
    
    /* Стан зовнішніх ресурсів (лише для Readiness!) */
    bool db_pool_connected;
    int available_db_conns;
    
    /* Прапорець вимкнення процесу (Graceful Shutdown) */
    bool is_draining;
    
    /* Лічильники для гістерезису */
    int consecutive_failures;
    int consecutive_successes;
    HealthStatus current_readiness;
    
    /* Кешовані звіти для захисту від шторму перевірок */
    HealthReport cached_liveness;
    HealthReport cached_readiness;
    
    pthread_mutex_t lock;
} HealthMonitor;

/* Отримання поточного часу в мілісекундах */
static uint64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

/* Ініціалізація монітора */
void health_monitor_init(HealthMonitor *mon, size_t mem_limit_mb, int max_workers) {
    mon->memory_used_mb = 50;
    mon->memory_limit_mb = mem_limit_mb;
    mon->active_workers = 1;
    mon->max_workers = max_workers;
    mon->db_pool_connected = true;
    mon->available_db_conns = 10;
    mon->is_draining = false;
    mon->consecutive_failures = 0;
    mon->consecutive_successes = SUCCESS_THRESHOLD;
    mon->current_readiness = HEALTH_STATUS_HEALTHY;

    memset(&mon->cached_liveness, 0, sizeof(HealthReport));
    memset(&mon->cached_readiness, 0, sizeof(HealthReport));
    pthread_mutex_init(&mon->lock, NULL);
}

void health_monitor_destroy(HealthMonitor *mon) {
    pthread_mutex_destroy(&mon->lock);
}

/* Переведення сервісу в режим вимкнення (Drain) */
void health_monitor_trigger_drain(HealthMonitor *mon) {
    pthread_mutex_lock(&mon->lock);
    mon->is_draining = true;
    /* Інвалідуємо кеш готовності для миттєвої реакції */
    mon->cached_readiness.evaluated_at_ms = 0;
    pthread_mutex_unlock(&mon->lock);
}

/* 1. LIVENESS CHECK: швидка локальна перевірка життєздатності процесу */
HealthReport health_check_liveness(HealthMonitor *mon) {
    pthread_mutex_lock(&mon->lock);
    uint64_t now = current_time_ms();

    /* Якщо кеш ще свіжий — повертаємо готовий результат */
    if (mon->cached_liveness.evaluated_at_ms > 0 && 
        (now - mon->cached_liveness.evaluated_at_ms) < CACHE_TTL_MS) {
        HealthReport cached = mon->cached_liveness;
        pthread_mutex_unlock(&mon->lock);
        return cached;
    }

    HealthReport report;
    report.evaluated_at_ms = now;

    /* Liveness перевіряє ТІЛЬКИ локальний процес: чи немає мертвого зависання пам'яті */
    if (mon->memory_used_mb > mon->memory_limit_mb) {
        report.status = HEALTH_STATUS_UNHEALTHY;
        report.http_code = 500;
        snprintf(report.details, sizeof(report.details),
                 "CRITICAL: Memory limit exceeded (%zu MB / %zu MB)",
                 mon->memory_used_mb, mon->memory_limit_mb);
    } else {
        report.status = HEALTH_STATUS_HEALTHY;
        report.http_code = 200;
        snprintf(report.details, sizeof(report.details),
                 "OK: Process alive (Mem: %zu/%zu MB, Workers: %d/%d)",
                 mon->memory_used_mb, mon->memory_limit_mb,
                 mon->active_workers, mon->max_workers);
    }

    mon->cached_liveness = report;
    pthread_mutex_unlock(&mon->lock);
    return report;
}

/* 2. READINESS CHECK: перевірка готовності приймати новий трафік */
HealthReport health_check_readiness(HealthMonitor *mon) {
    pthread_mutex_lock(&mon->lock);
    uint64_t now = current_time_ms();

    /* Перевірка валідності кешу */
    if (mon->cached_readiness.evaluated_at_ms > 0 && 
        (now - mon->cached_readiness.evaluated_at_ms) < CACHE_TTL_MS) {
        HealthReport cached = mon->cached_readiness;
        pthread_mutex_unlock(&mon->lock);
        return cached;
    }

    HealthReport report;
    report.evaluated_at_ms = now;

    /* Якщо сервіс вимикається — він миттєво не готовий приймати новий трафік */
    if (mon->is_draining) {
        report.status = HEALTH_STATUS_UNHEALTHY;
        report.http_code = 503;
        snprintf(report.details, sizeof(report.details), "SHUTDOWN: Node is draining traffic");
        mon->cached_readiness = report;
        pthread_mutex_unlock(&mon->lock);
        return report;
    }

    /* Оцінка факторів готовності */
    bool local_ready = (mon->db_pool_connected && mon->available_db_conns > 0);

    /* Гістерезисний фільтр для згладжування флапінгу */
    if (!local_ready) {
        mon->consecutive_failures++;
        mon->consecutive_successes = 0;
        if (mon->consecutive_failures >= FAILURE_THRESHOLD) {
            mon->current_readiness = HEALTH_STATUS_UNHEALTHY;
        }
    } else {
        mon->consecutive_successes++;
        mon->consecutive_failures = 0;
        if (mon->consecutive_successes >= SUCCESS_THRESHOLD) {
            mon->current_readiness = HEALTH_STATUS_HEALTHY;
        }
    }

    if (mon->current_readiness == HEALTH_STATUS_HEALTHY) {
        report.status = HEALTH_STATUS_HEALTHY;
        report.http_code = 200;
        snprintf(report.details, sizeof(report.details),
                 "OK: Ready for traffic (DB conns: %d)", mon->available_db_conns);
    } else {
        report.status = HEALTH_STATUS_UNHEALTHY;
        report.http_code = 503;
        snprintf(report.details, sizeof(report.details),
                 "UNAVAILABLE: DB pool exhausted or disconnected");
    }

    mon->cached_readiness = report;
    pthread_mutex_unlock(&mon->lock);
    return report;
}

int main(void) {
    HealthMonitor monitor;
    health_monitor_init(&monitor, 512, 16);

    printf("=== Демонстрація стійкого модуля перевірки ===\n\n");

    /* 1. Штатна перевірка */
    HealthReport l1 = health_check_liveness(&monitor);
    HealthReport r1 = health_check_readiness(&monitor);
    printf("[1] Liveness:  HTTP %d | %s\n", l1.http_code, l1.details);
    printf("    Readiness: HTTP %d | %s\n\n", r1.http_code, r1.details);

    /* 2. Тимчасовий збій пулу БД (імітація 1 збою — фільтрується гістерезисом) */
    monitor.available_db_conns = 0;
    monitor.cached_readiness.evaluated_at_ms = 0; /* скидаємо кеш для тесту */
    HealthReport r2 = health_check_readiness(&monitor);
    printf("[2] Збій БД (спроба 1): Readiness HTTP %d (гістерезис утримав вузол у ротації)\n", r2.http_code);

    /* 3. Серія збоїв — статус переходить у 503 */
    health_check_readiness(&monitor);
    monitor.cached_readiness.evaluated_at_ms = 0;
    HealthReport r3 = health_check_readiness(&monitor);
    printf("[3] Постійний збій (спроба 3): Readiness HTTP %d | %s\n\n", r3.http_code, r3.details);

    /* 4. Початок Graceful Shutdown */
    health_monitor_trigger_drain(&monitor);
    HealthReport r4 = health_check_readiness(&monitor);
    HealthReport l4 = health_check_liveness(&monitor);
    printf("[4] Сигнал SIGTERM (Drain):\n");
    printf("    Readiness: HTTP %d | %s (трафік знято)\n", r4.http_code, r4.details);
    printf("    Liveness:  HTTP %d | %s (процес залишається живим для завершення черги)\n", l4.http_code, l4.details);

    health_monitor_destroy(&monitor);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <mutex>
#include <atomic>
#include <format>
#include <cstdint>

enum class HealthStatus {
    Healthy,
    Degraded,
    Unhealthy
};

struct HealthReport {
    HealthStatus status{HealthStatus::Healthy};
    int http_code{200};
    std::chrono::steady_clock::time_point evaluated_at{};
    std::string details{};
};

class ResilientHealthMonitor {
public:
    explicit ResilientHealthMonitor(size_t memory_limit_mb, int max_workers)
        : memory_limit_mb_(memory_limit_mb), max_workers_(max_workers) {}

    // Ініціація граційного зняття трафіку під час отримання SIGTERM
    void trigger_drain() noexcept {
        is_draining_.store(true, std::memory_order_release);
        std::lock_guard<std::mutex> lock(mutex_);
        cached_readiness_.evaluated_at = std::chrono::steady_clock::time_point{};
    }

    void update_system_metrics(size_t mem_used_mb, int active_workers, 
                               bool db_ok, int db_conns) {
        std::lock_guard<std::mutex> lock(mutex_);
        memory_used_mb_ = mem_used_mb;
        active_workers_ = active_workers;
        db_pool_connected_ = db_ok;
        available_db_conns_ = db_conns;
    }

    // 1. Liveness: швидка перевірка внутрішнього стану процесу в пам'яті
    [[nodiscard]] HealthReport check_liveness() {
        const auto now = std::chrono::steady_clock::now();
        std::lock_guard<std::mutex> lock(mutex_);

        // Перевірка TTL кешу
        if (cached_liveness_.evaluated_at.time_since_epoch().count() > 0 &&
            (now - cached_liveness_.evaluated_at) < kCacheTtl) {
            return cached_liveness_;
        }

        HealthReport report;
        report.evaluated_at = now;

        if (memory_used_mb_ > memory_limit_mb_) {
            report.status = HealthStatus::Unhealthy;
            report.http_code = 500;
            report.details = "CRITICAL: Heap allocation exceeded limit";
        } else {
            report.status = HealthStatus::Healthy;
            report.http_code = 200;
            report.details = "OK: Process internal event loop healthy";
        }

        cached_liveness_ = report;
        return report;
    }

    // 2. Readiness: оцінка здатності приймати трафік користувачів
    [[nodiscard]] HealthReport check_readiness() {
        const auto now = std::chrono::steady_clock::now();
        std::lock_guard<std::mutex> lock(mutex_);

        if (cached_readiness_.evaluated_at.time_since_epoch().count() > 0 &&
            (now - cached_readiness_.evaluated_at) < kCacheTtl) {
            return cached_readiness_;
        }

        HealthReport report;
        report.evaluated_at = now;

        if (is_draining_.load(std::memory_order_acquire)) {
            report.status = HealthStatus::Unhealthy;
            report.http_code = 503;
            report.details = "SHUTDOWN: Instance is draining traffic";
            cached_readiness_ = report;
            return report;
        }

        const bool is_ready_now = (db_pool_connected_ && available_db_conns_ > 0);

        // Фільтрація миготіння (Hysteresis)
        if (!is_ready_now) {
            ++consecutive_failures_;
            consecutive_successes_ = 0;
            if (consecutive_failures_ >= kFailureThreshold) {
                current_readiness_ = HealthStatus::Unhealthy;
            }
        } else {
            ++consecutive_successes_;
            consecutive_failures_ = 0;
            if (consecutive_successes_ >= kSuccessThreshold) {
                current_readiness_ = HealthStatus::Healthy;
            }
        }

        if (current_readiness_ == HealthStatus::Healthy) {
            report.status = HealthStatus::Healthy;
            report.http_code = 200;
            report.details = "OK: Ready to serve traffic";
        } else {
            report.status = HealthStatus::Unhealthy;
            report.http_code = 503;
            report.details = "UNAVAILABLE: Resources exhausted or degraded";
        }

        cached_readiness_ = report;
        return report;
    }

private:
    static constexpr std::chrono::milliseconds kCacheTtl{2000};
    static constexpr int kFailureThreshold = 3;
    static constexpr int kSuccessThreshold = 2;

    std::mutex mutex_;
    size_t memory_used_mb_{64};
    size_t memory_limit_mb_{512};
    int active_workers_{2};
    int max_workers_{16};
    
    bool db_pool_connected_{true};
    int available_db_conns_{10};
    std::atomic<bool> is_draining_{false};

    int consecutive_failures_{0};
    int consecutive_successes_{kSuccessThreshold};
    HealthStatus current_readiness_{HealthStatus::Healthy};

    HealthReport cached_liveness_{};
    HealthReport cached_readiness_{};
};

int main() {
    ResilientHealthMonitor monitor(512, 16);

    std::cout << "=== C++20 Resilient Health Check Engine ===\n\n";

    auto liveness = monitor.check_liveness();
    auto readiness = monitor.check_readiness();

    std::cout << "[1] Liveness:  HTTP " << liveness.http_code << " (" << liveness.details << ")\n";
    std::cout << "    Readiness: HTTP " << readiness.http_code << " (" << readiness.details << ")\n\n";

    // Активація фази Drain
    monitor.trigger_drain();
    auto liveness_drain = monitor.check_liveness();
    auto readiness_drain = monitor.check_readiness();

    std::cout << "[2] Під час зупинки сервісу:\n";
    std::cout << "    Readiness: HTTP " << readiness_drain.http_code << " -> Балансувальник вилучає вузол\n";
    std::cout << "    Liveness:  HTTP " << liveness_drain.http_code  << " -> Оркестратор НЕ вбиває под до завершення з'єднань\n";

    return 0;
}
```
:::

## Аналіз архітектурних деталей реалізації

Порівняння двох реалізацій демонструє різницю системних моделей керування ресурсами:

### 1. Синхронізація та час життя об'єктів у C проти C++
* У версії мовою C синхронізація виконується за допомогою POSIX-м'ютекса `pthread_mutex_t`, що вимагає явної ініціалізації та ручного виклику `pthread_mutex_destroy()`. Для представлення міток часу використовується монотонний системний таймер `clock_gettime(CLOCK_MONOTONIC)`.
* У версії мовою C++ застосовано ідіому **RAII** та механізм `std::lock_guard<std::mutex>`, який гарантує автоматичне звільнення блокування при виході з області видимості функції навіть у разі генерації винятків. Для монотонного вимірювання часу використано типізований інтерфейс `std::chrono::steady_clock`.

### 2. Атомарне зняття трафіку (Drain Coordination)
В обох мовах прапорець `is_draining` є критичною точкою синхронізації. У C++ він оголошений як `std::atomic<bool>` із явною семантикою пам'яті `memory_order_release` під час запису в обробнику сигналу та `memory_order_acquire` під час читання в обробнику запиту. Це гарантує, що всі попередні модифікації пам'яті процесу стануть видимими для інших потоків без потреби захоплення важких блокувань.

### 3. Ефективність кешування та захист від сплесків (Debouncing)
Кешування з константою `CACHE_TTL_MS = 2000` зрізає 99% навантаження від частих перевірок оркестратора та моніторингових систем Prometheus / Datadog. Навіть при частоті 500 запитів на секунду до ендпоінта `/healthz`, важка перевірка внутрішніх підсистем виконуватиметься лише двічі на секунду, захищаючи процесор та пам'ять від непродуктивних витрат.
