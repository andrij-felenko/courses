#include "a3144.h"
#include <stddef.h>

bool a3144_init(a3144_handle_t *handle, const a3144_config_t *config) {
    if (handle == NULL || config == NULL) {
        return false;
    }

    if (config->pulses_per_rev == 0) {
        return false;
    }

    handle->config = *config;
    handle->state = A3144_STATE_IDLE;
    handle->approach_flag = false;
    handle->removal_flag = false;
    handle->trigger_count = 0;
    handle->last_interrupt_ms = 0;
    handle->pulse_period_ms = 0;
    handle->current_rpm = 0.0f;
    handle->last_rpm_update_ms = 0;

    return true;
}

void a3144_exti_isr_handler(a3144_handle_t *handle, uint32_t current_time_ms, bool is_pin_low) {
    if (handle == NULL) {
        return;
    }

    /* Програмне придушення брязкоту за часовим інтервалом */
    uint32_t elapsed = current_time_ms - handle->last_interrupt_ms;
    if (handle->last_interrupt_ms != 0 && elapsed < handle->config.debounce_ms) {
        return;
    }

    if (is_pin_low) {
        /* Сигнал LOW — магніт наблизився (спрацювання кінцевого вимикача) */
        if (handle->state != A3144_STATE_MAGNET_ACTIVE) {
            handle->state = A3144_STATE_MAGNET_ACTIVE;
            handle->approach_flag = true;
            handle->trigger_count++;

            /* Розрахунок періоду між імпульсами для розрахунку RPM */
            if (handle->last_interrupt_ms != 0) {
                handle->pulse_period_ms = elapsed;
            }
        }
    } else {
        /* Сигнал HIGH — магніт віддалився (розмикання кінцевого вимикача) */
        if (handle->state != A3144_STATE_IDLE) {
            handle->state = A3144_STATE_IDLE;
            handle->removal_flag = true;
        }
    }

    handle->last_interrupt_ms = current_time_ms;
}

void a3144_process(a3144_handle_t *handle, uint32_t current_time_ms) {
    if (handle == NULL) {
        return;
    }

    /* Розрахунок RPM за наявним періодом імпульсів */
    if (handle->pulse_period_ms > 0) {
        /* RPM = (60000 мс / період_мс) / імпульсів_на_оберт */
        float period_sec = (float)handle->pulse_period_ms / 1000.0f;
        float revs_per_sec = (1.0f / period_sec) / (float)handle->config.pulses_per_rev;
        handle->current_rpm = revs_per_sec * 60.0f;
    }

    /* Таймаут відсутності обертання: якщо магніт довго не проходить, RPM = 0 */
    uint32_t idle_time = current_time_ms - handle->last_interrupt_ms;
    if (handle->config.rpm_timeout_ms > 0 && handle->last_interrupt_ms != 0) {
        if (idle_time > handle->config.rpm_timeout_ms) {
            handle->current_rpm = 0.0f;
            handle->pulse_period_ms = 0;
        }
    }
}

bool a3144_is_magnet_present(const a3144_handle_t *handle) {
    if (handle == NULL) {
        return false;
    }
    return (handle->state == A3144_STATE_MAGNET_ACTIVE);
}

bool a3144_get_approach_event(a3144_handle_t *handle) {
    if (handle == NULL) {
        return false;
    }
    if (handle->approach_flag) {
        handle->approach_flag = false;
        return true;
    }
    return false;
}

bool a3144_get_removal_event(a3144_handle_t *handle) {
    if (handle == NULL) {
        return false;
    }
    if (handle->removal_flag) {
        handle->removal_flag = false;
        return true;
    }
    return false;
}

uint32_t a3144_get_trigger_count(const a3144_handle_t *handle) {
    if (handle == NULL) {
        return 0;
    }
    return handle->trigger_count;
}

float a3144_get_rpm(const a3144_handle_t *handle) {
    if (handle == NULL) {
        return 0.0f;
    }
    return handle->current_rpm;
}

void a3144_reset_counters(a3144_handle_t *handle) {
    if (handle == NULL) {
        return;
    }
    handle->trigger_count = 0;
    handle->current_rpm = 0.0f;
    handle->pulse_period_ms = 0;
}
