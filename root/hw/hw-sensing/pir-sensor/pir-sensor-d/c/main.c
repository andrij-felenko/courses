#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t debounce_ms;
    uint32_t hold_time_ms;
    uint32_t last_edge_time_ms;
    uint32_t motion_start_time_ms;
    bool raw_state;
    bool stable_state;
    bool motion_active;
} pir_digital_detector_t;

void pir_digital_init(pir_digital_detector_t *det, uint32_t debounce_ms, uint32_t hold_time_ms) {
    det->debounce_ms = debounce_ms;
    det->hold_time_ms = hold_time_ms;
    det->last_edge_time_ms = 0;
    det->motion_start_time_ms = 0;
    det->raw_state = false;
    det->stable_state = false;
    det->motion_active = false;
}

bool pir_digital_update(pir_digital_detector_t *det, bool pin_level, uint32_t current_time_ms) {
    bool event_triggered = false;

    // Фіксація зміни фізичного рівня на вході
    if (pin_level != det->raw_state) {
        det->raw_state = pin_level;
        det->last_edge_time_ms = current_time_ms;
    }

    // Програмна фільтрація брязкоту контактів та коротких перешкод
    if ((current_time_ms - det->last_edge_time_ms) >= det->debounce_ms) {
        if (det->raw_state != det->stable_state) {
            det->stable_state = det->raw_state;

            if (det->stable_state) {
                // Передній фронт: підтверджено початок руху
                det->motion_active = true;
                det->motion_start_time_ms = current_time_ms;
                event_triggered = true;
            }
        }
    }

    // Автоматичне утримання прапорця руху в режимі перезапуску
    if (det->motion_active) {
        if (det->stable_state) {
            det->motion_start_time_ms = current_time_ms;
        } else if ((current_time_ms - det->motion_start_time_ms) >= det->hold_time_ms) {
            det->motion_active = false;
        }
    }

    return event_triggered;
}

bool pir_digital_is_occupied(const pir_digital_detector_t *det) {
    return det->motion_active;
}
