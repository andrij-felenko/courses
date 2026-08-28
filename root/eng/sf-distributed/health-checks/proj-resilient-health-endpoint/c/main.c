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
