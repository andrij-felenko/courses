#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include <pthread.h>
#include <time.h>
#include <math.h>

#define DEFAULT_MIN_LIMIT 5.0
#define DEFAULT_MAX_LIMIT 1000.0
#define DEFAULT_INITIAL_LIMIT 20.0
#define DEFAULT_WINDOW_SIZE 50
#define DEFAULT_MIN_RTT_TTL_SEC 300.0 /* 5 хвилин */

typedef struct {
    double min_limit;          /* мінімальна межа паралелізму */
    double max_limit;          /* максимальна межа паралелізму */
    double headroom;           /* параметр запасу черги h */
    double smoothing;          /* коефіцієнт експоненційного згладжування σ */
    uint32_t sample_window;    /* кількість запитів на одне вікно вибірки */
    double min_rtt_ttl_sec;    /* тривалість життя базового minRTT */
} vegas_config_t;

typedef struct {
    vegas_config_t cfg;
    atomic_int in_flight;

    pthread_mutex_t lock;
    double current_limit;

    /* Поточне вікно вибірки */
    uint32_t sample_count;
    double sample_rtt_sum_ms;

    /* Базова затримка */
    double min_rtt_ms;
    double min_rtt_timestamp_sec;
} vegas_limiter_t;

static double get_monotonic_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

vegas_limiter_t* vegas_limiter_create(const vegas_config_t* cfg) {
    vegas_limiter_t* lim = (vegas_limiter_t*)calloc(1, sizeof(vegas_limiter_t));
    if (!lim) return NULL;

    lim->cfg = *cfg;
    atomic_init(&lim->in_flight, 0);
    pthread_mutex_init(&lim->lock, NULL);

    lim->current_limit = cfg->min_limit > 0 ? cfg->min_limit : DEFAULT_INITIAL_LIMIT;
    lim->min_rtt_ms = -1.0; /* ще не ініціалізовано */
    lim->min_rtt_timestamp_sec = get_monotonic_time_sec();
    return lim;
}

void vegas_limiter_destroy(vegas_limiter_t* lim) {
    if (!lim) return;
    pthread_mutex_destroy(&lim->lock);
    free(lim);
}

/* Спроба допуску запиту (Lock-free перевірка атомарного лічильника) */
bool vegas_limiter_acquire(vegas_limiter_t* lim, double* out_start_time) {
    int current = atomic_load_explicit(&lim->in_flight, memory_order_relaxed);
    
    /* Читання поточного ліміту для швидкого відсікання */
    double limit = lim->current_limit;
    if ((double)current >= limit) {
        return false; /* Швидке відхилення надлишку: 429 Too Many Requests */
    }

    /* Атомарне інкрементування активних запитів */
    atomic_fetch_add_explicit(&lim->in_flight, 1, memory_order_acq_rel);
    *out_start_time = get_monotonic_time_sec();
    return true;
}

/* Фіксація завершення запиту та оновлення моделі */
void vegas_limiter_release(vegas_limiter_t* lim, double start_time, bool success) {
    double now = get_monotonic_time_sec();
    double duration_ms = (now - start_time) * 1000.0;

    atomic_fetch_sub_explicit(&lim->in_flight, 1, memory_order_acq_rel);

    /* Неуспішні запити (мережеві обриви, дедлайни) не повинні спотворювати RTT */
    if (!success || duration_ms <= 0.0) {
        return;
    }

    pthread_mutex_lock(&lim->lock);

    /* Оновлення або планове старіння minRTT */
    if (lim->min_rtt_ms < 0.0 || (now - lim->min_rtt_timestamp_sec) > lim->cfg.min_rtt_ttl_sec) {
        lim->min_rtt_ms = duration_ms;
        lim->min_rtt_timestamp_sec = now;
    } else if (duration_ms < lim->min_rtt_ms) {
        lim->min_rtt_ms = duration_ms;
    }

    lim->sample_count++;
    lim->sample_rtt_sum_ms += duration_ms;

    /* Закриття вікна вибірки та перерахунок ліміту */
    if (lim->sample_count >= lim->cfg.sample_window) {
        double sample_rtt = lim->sample_rtt_sum_ms / (double)lim->sample_count;
        double min_rtt = lim->min_rtt_ms;

        if (sample_rtt > 0.0 && min_rtt > 0.0) {
            double gradient = min_rtt / sample_rtt;
            
            /* Обчислення цільового ліміту за формулою Vegas */
            double target_limit = lim->current_limit * gradient + lim->cfg.headroom;
            
            /* Експоненційне згладжування */
            double next_limit = (1.0 - lim->cfg.smoothing) * lim->current_limit 
                              + lim->cfg.smoothing * target_limit;

            /* Обмеження діапазоном безпеки */
            if (next_limit < lim->cfg.min_limit) next_limit = lim->cfg.min_limit;
            if (next_limit > lim->cfg.max_limit) next_limit = lim->cfg.max_limit;

            lim->current_limit = next_limit;
        }

        lim->sample_count = 0;
        lim->sample_rtt_sum_ms = 0.0;
    }

    pthread_mutex_unlock(&lim->lock);
}
