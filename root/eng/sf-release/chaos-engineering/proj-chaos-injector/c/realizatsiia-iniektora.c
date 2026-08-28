#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <sys/timerfd.h>
#include <sys/signalfd.h>
#include <signal.h>
#include <time.h>

/* Стан скінченного автомата експерименту */
typedef enum {
    CHAOS_STATE_IDLE = 0,
    CHAOS_STATE_RUNNING,
    CHAOS_STATE_ABORTED,
    CHAOS_STATE_COMPLETED
} chaos_state_t;

/* Конфігурація хаос-ін'єкції */
typedef struct {
    uint32_t duration_sec;       /* Загальний час експерименту */
    uint32_t delay_ms;           /* Штучна затримка */
    uint32_t failure_rate_pct;   /* Відсоток штучних помилок (0-100) */
    double   max_allowed_err_pct;/* Критичний поріг для Kill Switch */
} chaos_config_t;

/* Структура координатора */
typedef struct {
    chaos_config_t   config;
    _Atomic int      state;
    _Atomic uint64_t total_requests;
    _Atomic uint64_t failed_requests;
    int              timer_fd;
    pthread_t        worker_thread;
    pthread_t        monitor_thread;
} chaos_coordinator_t;

/* Безпечний сон у мілісекундах */
static void sleep_ms(uint32_t ms) {
    struct timespec ts;
    ts.tv_sec = ms / 1000;
    ts.tv_nsec = (ms % 1000) * 1000000L;
    nanosleep(&ts, NULL);
}

/* Ініціалізація сторожового таймера через timerfd */
static int init_watchdog_timer(uint32_t seconds) {
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    if (tfd < 0) {
        perror("timerfd_create failed");
        return -1;
    }
    struct itimerspec its;
    memset(&its, 0, sizeof(its));
    its.it_value.tv_sec = seconds;
    its.it_value.tv_nsec = 0;
    if (timerfd_settime(tfd, 0, &its, NULL) < 0) {
        perror("timerfd_settime failed");
        close(tfd);
        return -1;
    }
    return tfd;
}

/* Ідемпотентна функція відкату правил та згортання */
static void chaos_rollback(chaos_coordinator_t *coord, const char *reason) {
    int expected = CHAOS_STATE_RUNNING;
    if (atomic_compare_exchange_strong(&coord->state, &expected, CHAOS_STATE_ABORTED)) {
        printf("\n[ROLLBACK] Аварійна зупинка хаос-ін'єкції! Причина: %s\n", reason);
        printf("[ROLLBACK] Відновлення мережевих правил та зняття обмежень...\n");
        /* Симуляція відновлення правил Linux TC або скидання envoy filter */
        printf("[ROLLBACK] Стан системи повернуто до базової лінії (Clean).\n");
    }
}

/* Потік моніторингу SLI та сторожового таймера */
static void *monitor_thread_fn(void *arg) {
    chaos_coordinator_t *coord = (chaos_coordinator_t *)arg;
    uint64_t exp_buf;

    while (atomic_load(&coord->state) == CHAOS_STATE_RUNNING) {
        /* Перевірка спрацювання дедлайну timerfd */
        ssize_t s = read(coord->timer_fd, &exp_buf, sizeof(exp_buf));
        if (s == sizeof(exp_buf)) {
            chaos_rollback(coord, "Вичерпано ліміт часу експерименту (Watchdog TTL)");
            break;
        }

        /* Перевірка індикатора стійкого стану (SLI) */
        uint64_t total = atomic_load(&coord->total_requests);
        uint64_t failed = atomic_load(&coord->failed_requests);
        if (total > 20) {
            double current_err_pct = ((double)failed / (double)total) * 100.0;
            if (current_err_pct > coord->config.max_allowed_err_pct) {
                char reason[128];
                snprintf(reason, sizeof(reason), "Порушення SLO! Помилки: %.2f%% (ліміт: %.2f%%)",
                         current_err_pct, coord->config.max_allowed_err_pct);
                chaos_rollback(coord, reason);
                break;
            }
        }
        sleep_ms(100);
    }
    return NULL;
}

/* Робочий потік: симуляція проходження клієнтських транзакцій */
static void *worker_thread_fn(void *arg) {
    chaos_coordinator_t *coord = (chaos_coordinator_t *)arg;

    while (atomic_load(&coord->state) == CHAOS_STATE_RUNNING) {
        atomic_fetch_add(&coord->total_requests, 1);
        int roll = rand() % 100;

        if (roll < (int)coord->config.failure_rate_pct) {
            /* Ін'єкція збою: затримка та повернення коду помилки */
            sleep_ms(coord->config.delay_ms);
            atomic_fetch_add(&coord->failed_requests, 1);
            printf("[WORKER] Ін'єкція: затримка %ums -> Помилка 503 (відмова)\n", coord->config.delay_ms);
        } else {
            /* Нормальна обробка запиту */
            sleep_ms(15);
            printf("[WORKER] Запит оброблено штатно (200 OK)\n");
        }
        sleep_ms(50);
    }
    return NULL;
}

int main(void) {
    srand((unsigned int)time(NULL));
    printf("=== Запуск системного координатора хаос-експериментів (C POSIX) ===\n");

    chaos_coordinator_t coord;
    memset(&coord, 0, sizeof(coord));
    coord.config.duration_sec = 4;
    coord.config.delay_ms = 120;
    coord.config.failure_rate_pct = 35;
    coord.config.max_allowed_err_pct = 30.0; /* Поріг аварійного відкату */

    atomic_store(&coord.state, CHAOS_STATE_RUNNING);
    coord.timer_fd = init_watchdog_timer(coord.config.duration_sec);
    if (coord.timer_fd < 0) {
        return EXIT_FAILURE;
    }

    pthread_create(&coord.monitor_thread, NULL, monitor_thread_fn, &coord);
    pthread_create(&coord.worker_thread, NULL, worker_thread_fn, &coord);

    /* Очікування завершення роботи потоків */
    pthread_join(coord.monitor_thread, NULL);
    pthread_join(coord.worker_thread, NULL);

    int final_state = atomic_load(&coord->state);
    if (final_state == CHAOS_STATE_RUNNING) {
        int expected = CHAOS_STATE_RUNNING;
        atomic_compare_exchange_strong(&coord->state, &expected, CHAOS_STATE_COMPLETED);
        printf("\n[SUCCESS] Хаос-експеримент завершено штатно без порушення SLO.\n");
    }

    uint64_t total = atomic_load(&coord->total_requests);
    uint64_t failed = atomic_load(&coord->failed_requests);
    printf("Підсумок: %lu запитів, %lu помилок (%.2f%%)\n",
           total, failed, total ? ((double)failed / (double)total) * 100.0 : 0.0);

    close(coord.timer_fd);
    return EXIT_SUCCESS;
}
