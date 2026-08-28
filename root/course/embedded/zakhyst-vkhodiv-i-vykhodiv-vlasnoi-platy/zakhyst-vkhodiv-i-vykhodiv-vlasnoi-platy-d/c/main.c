// Драйвер моніторингу апаратного захисту та антибрязкоту (C99)
#include <stdint.h>
#include <stdbool.h>

#define DEBOUNCE_THRESHOLD_MS  20U
#define FAULT_RETRY_LIMIT      3U

typedef enum {
    PORT_STATE_NORMAL = 0,
    PORT_STATE_OVERCURRENT,
    PORT_STATE_OVERVOLTAGE,
    PORT_STATE_LATCHED_FAULT
} port_protection_status_t;

typedef struct {
    uint32_t last_stable_time_ms;
    uint8_t  raw_state_history;
    bool     debounced_state;
} input_filter_t;

typedef struct {
    port_protection_status_t status;
    uint8_t fault_retries;
    uint32_t last_fault_time_ms;
    bool output_enabled;
} output_guard_t;

// Обробка дискретного входу з інтегруючим фільтром брязкоту
bool input_filter_update(input_filter_t *filter, bool current_raw_pin, uint32_t current_time_ms) {
    // Зсув історії стану піна (маска на 8 відліків)
    filter->raw_state_history = (uint8_t)((filter->raw_state_history << 1) | (current_raw_pin ? 1U : 0U));
    
    if (filter->raw_state_history == 0xFFU) {
        if (!filter->debounced_state && (current_time_ms - filter->last_stable_time_ms >= DEBOUNCE_THRESHOLD_MS)) {
            filter->debounced_state = true;
            filter->last_stable_time_ms = current_time_ms;
        }
    } else if (filter->raw_state_history == 0x00U) {
        if (filter->debounced_state && (current_time_ms - filter->last_stable_time_ms >= DEBOUNCE_THRESHOLD_MS)) {
            filter->debounced_state = false;
            filter->last_stable_time_ms = current_time_ms;
        }
    }
    return filter->debounced_state;
}

// Моніторинг лінії FAULT смарт-ключа силового виходу
void output_guard_poll(output_guard_t *guard, bool is_fault_pin_active, uint32_t current_time_ms) {
    if (is_fault_pin_active && guard->output_enabled) {
        // Миттєве апаратне вимкнення виходу при сигналі КЗ або перегріву
        guard->output_enabled = false;
        guard->last_fault_time_ms = current_time_ms;
        guard->fault_retries++;
        
        if (guard->fault_retries >= FAULT_RETRY_LIMIT) {
            guard->status = PORT_STATE_LATCHED_FAULT;
        } else {
            guard->status = PORT_STATE_OVERCURRENT;
        }
    }
    
    // Спроба автоматичного перезапуску через 5 секунд при невиснаженому ліміті
    if (!guard->output_enabled && (guard->status == PORT_STATE_OVERCURRENT)) {
        if (current_time_ms - guard->last_fault_time_ms >= 5000U) {
            guard->output_enabled = true;
            guard->status = PORT_STATE_NORMAL;
        }
    }
}
