#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include <time.h>
#include <math.h>
#include <pthread.h>

typedef enum {
    PRIO_LOW    = 0,
    PRIO_NORMAL = 1,
    PRIO_HIGH   = 2
} RequestPriority;

typedef struct {
    atomic_int in_flight;
    atomic_int limit;
    int min_limit;
    int max_limit;
    
    double min_rtt_ms;
    double smoothed_rtt_ms;
    double smoothing_factor;
    double headroom;
    
    pthread_mutex_t metrics_lock;
} AdmissionController;

void admission_init(AdmissionController* ac, int min_limit, int max_limit) {
    atomic_init(&ac->in_flight, 0);
    atomic_init(&ac->limit, min_limit);
    ac->min_limit = min_limit;
    ac->max_limit = max_limit;
    ac->min_rtt_ms = 0.0;
    ac->smoothed_rtt_ms = 0.0;
    ac->smoothing_factor = 0.1;
    ac->headroom = 1.0;
    pthread_mutex_init(&ac->metrics_lock, NULL);
}

void admission_destroy(AdmissionController* ac) {
    pthread_mutex_destroy(&ac->metrics_lock);
}

int64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + (ts.tv_nsec / 1000000);
}

bool admission_try_acquire(AdmissionController* ac, RequestPriority prio, int64_t deadline_ms) {
    int64_t now = current_time_ms();
    
    /* 1. Перевірка дедлайну: якщо запит уже прострочений у черзі, відхиляємо */
    if (deadline_ms > 0 && now >= deadline_ms) {
        return false;
    }
    
    int cur_limit = atomic_load_explicit(&ac->limit, memory_order_relaxed);
    int current_in_flight = atomic_load_explicit(&ac->in_flight, memory_order_relaxed);
    
    /* 2. Пріоритетне скидання: низький пріоритет відсікається при 80% ліміту */
    if (prio == PRIO_LOW && current_in_flight >= (int)(cur_limit * 0.8)) {
        return false;
    }
    if (prio == PRIO_NORMAL && current_in_flight >= (int)(cur_limit * 0.95)) {
        return false;
    }
    
    /* 3. Атомарне захоплення слота за допомогою CAS-циклу */
    while (current_in_flight < cur_limit) {
        if (atomic_compare_exchange_weak_explicit(&ac->in_flight, 
                                                  &current_in_flight, 
                                                  current_in_flight + 1,
                                                  memory_order_acquire,
                                                  memory_order_relaxed)) {
            return true;
        }
    }
    
    return false;
}

void admission_release(AdmissionController* ac, double duration_ms) {
    atomic_fetch_sub_explicit(&ac->in_flight, 1, memory_order_release);
    
    pthread_mutex_lock(&ac->metrics_lock);
    
    /* Оновлення мінімального базового часу відгуку */
    if (ac->min_rtt_ms <= 0.0 || duration_ms < ac->min_rtt_ms) {
        ac->min_rtt_ms = duration_ms;
    }
    
    /* Експоненційне згладжування поточної затримки (EWMA) */
    if (ac->smoothed_rtt_ms <= 0.0) {
        ac->smoothed_rtt_ms = duration_ms;
    } else {
        ac->smoothed_rtt_ms = (1.0 - ac->smoothing_factor) * ac->smoothed_rtt_ms 
                            + ac->smoothing_factor * duration_ms;
    }
    
    /* Розрахунок градієнта та оновлення ліміту */
    if (ac->min_rtt_ms > 0.0 && ac->smoothed_rtt_ms > 0.0) {
        double gradient = ac->min_rtt_ms / ac->smoothed_rtt_ms;
        if (gradient > 1.0) gradient = 1.0;
        
        int cur_limit = atomic_load_explicit(&ac->limit, memory_order_relaxed);
        double new_limit = (double)cur_limit * gradient + ac->headroom;
        
        int target = (int)round(new_limit);
        if (target < ac->min_limit) target = ac->min_limit;
        if (target > ac->max_limit) target = ac->max_limit;
        
        atomic_store_explicit(&ac->limit, target, memory_order_relaxed);
    }
    
    pthread_mutex_unlock(&ac->metrics_lock);
}
