#include <stdint.h>
#include <stdbool.h>

typedef struct {
    float    upper_threshold;      /* Поріг активації умови (S_on) */
    float    lower_threshold;      /* Поріг деактивації умови (S_off) */
    uint32_t debounce_time_us;     /* Час підтвердження істинності умови */
    uint32_t dwell_time_us;        /* Мінімальний час утримання активного стану */
    uint32_t condition_start_us;   /* Мітка часу початку виконання умови */
    uint32_t state_entered_us;     /* Мітка часу останнього перемикання стану */
    bool     schmitt_state;        /* Поточний стан тригера Шмітта */
    bool     pending_activation;   /* Прапорець очікування завершення Debounce */
    bool     current_state;        /* Результуючий фільтрований стан виходу */
} goal_transition_filter_t;

void goal_transition_filter_init(goal_transition_filter_t *filter,
                                float upper_th, float lower_th,
                                uint32_t debounce_us, uint32_t dwell_us,
                                uint32_t now_us)
{
    filter->upper_threshold = upper_th;
    filter->lower_threshold = lower_th;
    filter->debounce_time_us = debounce_us;
    filter->dwell_time_us = dwell_us;
    filter->condition_start_us = 0;
    filter->state_entered_us = now_us;
    filter->schmitt_state = false;
    filter->pending_activation = false;
    filter->current_state = false;
}

bool goal_transition_filter_update(goal_transition_filter_t *filter,
                                  float metric_value,
                                  uint32_t now_us,
                                  bool emergency_override)
{
    /* 0. Обробка аварійного переривання нульового рангу */
    if (emergency_override) {
        filter->current_state = false;
        filter->schmitt_state = false;
        filter->pending_activation = false;
        filter->state_entered_us = now_us;
        return false;
    }

    /* 1. Скалярний гістерезис (програмний тригер Шмітта) */
    if (filter->schmitt_state) {
        if (metric_value <= filter->lower_threshold) {
            filter->schmitt_state = false;
        }
    } else {
        if (metric_value >= filter->upper_threshold) {
            filter->schmitt_state = true;
        }
    }

    /* 2. Логіка таймерів Debounce та Dwell */
    if (filter->current_state) {
        /* Стан АКТИВНИЙ: перевіряємо можливість виходу */
        if (!filter->schmitt_state) {
            const uint32_t time_in_state = now_us - filter->state_entered_us;
            if (time_in_state >= filter->dwell_time_us) {
                filter->current_state = false;
                filter->state_entered_us = now_us;
                filter->pending_activation = false;
            }
        } else {
            filter->pending_activation = false;
        }
    } else {
        /* Стан НЕАКТИВНИЙ: перевіряємо фільтрацію фронту входу (Debounce) */
        if (filter->schmitt_state) {
            if (!filter->pending_activation) {
                filter->pending_activation = true;
                filter->condition_start_us = now_us;
            } else {
                const uint32_t debounce_elapsed = now_us - filter->condition_start_us;
                if (debounce_elapsed >= filter->debounce_time_us) {
                    filter->current_state = true;
                    filter->state_entered_us = now_us;
                    filter->pending_activation = false;
                }
            }
        } else {
            filter->pending_activation = false;
        }
    }

    return filter->current_state;
}
