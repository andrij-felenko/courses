#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>

/* Класи пріоритетів запиту */
typedef enum {
    PRIORITY_P0_CRITICAL   = 0,
    PRIORITY_P1_HIGH       = 1,
    PRIORITY_P2_MEDIUM     = 2,
    PRIORITY_P3_LOW        = 3,
    PRIORITY_P4_BACKGROUND = 4
} request_priority_t;

/* Рівні деградації Brownout */
typedef enum {
    BROWNOUT_L0_NORMAL    = 0,
    BROWNOUT_L1_SHED_P4   = 1,
    BROWNOUT_L2_SHED_P3   = 2,
    BROWNOUT_L3_SHED_P2   = 3,
    BROWNOUT_L4_EMERGENCY = 4
} brownout_level_t;

/* Структура стану контролера скидання */
typedef struct {
    atomic_int active_requests;
    int max_capacity;
    atomic_int current_level;
    int hysteresis_delta;
} shedding_controller_t;

/* Результат оцінки прийому */
typedef struct {
    bool allow;
    int http_status;
    int retry_after_sec;
    const char* reason;
} admission_result_t;

void shedding_controller_init(shedding_controller_t *ctrl, int capacity) {
    atomic_init(&ctrl->active_requests, 0);
    ctrl->max_capacity = capacity;
    atomic_init(&ctrl->current_level, BROWNOUT_L0_NORMAL);
    ctrl->hysteresis_delta = 5;
}

/* Оновлення рівня Brownout з урахуванням гістерезису */
static void update_brownout_level(shedding_controller_t *ctrl) {
    int active = atomic_load_explicit(&ctrl->active_requests, memory_order_relaxed);
    int current = atomic_load_explicit(&ctrl->current_level, memory_order_relaxed);
    int next = current;

    /* Перевірка умов підвищення рівня тиску */
    if (active >= 95 && current < BROWNOUT_L4_EMERGENCY) {
        next = BROWNOUT_L4_EMERGENCY;
    } else if (active >= 85 && current < BROWNOUT_L3_SHED_P2) {
        next = BROWNOUT_L3_SHED_P2;
    } else if (active >= 70 && current < BROWNOUT_L2_SHED_P3) {
        next = BROWNOUT_L2_SHED_P3;
    } else if (active >= 50 && current < BROWNOUT_L1_SHED_P4) {
        next = BROWNOUT_L1_SHED_P4;
    }
    
    /* Перевірка умов зниження рівня з урахуванням гістерезису */
    else if (current == BROWNOUT_L4_EMERGENCY && active < (95 - ctrl->hysteresis_delta)) {
        next = BROWNOUT_L3_SHED_P2;
    } else if (current == BROWNOUT_L3_SHED_P2 && active < (85 - ctrl->hysteresis_delta)) {
        next = BROWNOUT_L2_SHED_P3;
    } else if (current == BROWNOUT_L2_SHED_P3 && active < (70 - ctrl->hysteresis_delta)) {
        next = BROWNOUT_L1_SHED_P4;
    } else if (current == BROWNOUT_L1_SHED_P4 && active < (50 - ctrl->hysteresis_delta)) {
        next = BROWNOUT_L0_NORMAL;
    }

    if (next != current) {
        atomic_store_explicit(&ctrl->current_level, next, memory_order_relaxed);
    }
}

/* Перевірка допустимості виклику */
admission_result_t shedding_controller_eval(shedding_controller_t *ctrl, request_priority_t prio) {
    update_brownout_level(ctrl);
    int lvl = atomic_load_explicit(&ctrl->current_level, memory_order_relaxed);

    admission_result_t res = {
        .allow = true,
        .http_status = 200,
        .retry_after_sec = 0,
        .reason = "Request admitted"
    };

    bool should_drop = false;
    switch (lvl) {
        case BROWNOUT_L4_EMERGENCY:
            if (prio > PRIORITY_P0_CRITICAL) should_drop = true;
            break;
        case BROWNOUT_L3_SHED_P2:
            if (prio >= PRIORITY_P2_MEDIUM) should_drop = true;
            break;
        case BROWNOUT_L2_SHED_P3:
            if (prio >= PRIORITY_P3_LOW) should_drop = true;
            break;
        case BROWNOUT_L1_SHED_P4:
            if (prio >= PRIORITY_P4_BACKGROUND) should_drop = true;
            break;
        case BROWNOUT_L0_NORMAL:
        default:
            should_drop = false;
            break;
    }

    if (should_drop) {
        res.allow = false;
        res.http_status = 503;
        res.retry_after_sec = 10 + ((int)prio * 5);
        res.reason = "Shedded due to active brownout level";
    } else {
        atomic_fetch_add_explicit(&ctrl->active_requests, 1, memory_order_relaxed);
    }

    return res;
}

/* Звільнення ресурсу після завершення обробки */
void shedding_controller_release(shedding_controller_t *ctrl) {
    int prev = atomic_fetch_sub_explicit(&ctrl->active_requests, 1, memory_order_relaxed);
    if (prev <= 0) {
        atomic_store_explicit(&ctrl->active_requests, 0, memory_order_relaxed);
    }
    update_brownout_level(ctrl);
}

int main(void) {
    shedding_controller_t ctrl;
    shedding_controller_init(&ctrl, 100);

    /* Імітація зростання навантаження до 75 паралельних запитів */
    atomic_store(&ctrl.active_requests, 75);

    /* Спроба виконати запит P4 (Background) під тиском */
    admission_result_t r_p4 = shedding_controller_eval(&ctrl, PRIORITY_P4_BACKGROUND);
    printf("P4 Request: allow=%d, status=%d, retry_after=%ds, reason='%s'\n",
           r_p4.allow, r_p4.http_status, r_p4.retry_after_sec, r_p4.reason);

    /* Спроба виконати запит P0 (Critical) під тиском */
    admission_result_t r_p0 = shedding_controller_eval(&ctrl, PRIORITY_P0_CRITICAL);
    printf("P0 Request: allow=%d, status=%d, active_requests=%d\n",
           r_p0.allow, r_p0.http_status, atomic_load(&ctrl.active_requests));

    shedding_controller_release(&ctrl);
    return 0;
}
