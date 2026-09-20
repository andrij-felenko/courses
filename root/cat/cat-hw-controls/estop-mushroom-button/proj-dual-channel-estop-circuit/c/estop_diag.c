#include "estop_diag.h"
#include <stddef.h>

void estop_diag_init(estop_diag_t *diag, bool (*read_gpio_fn)(void), uint32_t debounce_ms)
{
    if (diag == NULL || read_gpio_fn == NULL) {
        return;
    }

    diag->state = ESTOP_STATE_NORMAL;
    diag->read_gpio_fn = read_gpio_fn;
    diag->debounce_delay_ms = (debounce_ms > 0) ? debounce_ms : 20U;
    diag->last_raw_level = read_gpio_fn();
    diag->is_tripped = diag->last_raw_level;
    diag->last_state_change_ms = 0U;
    diag->total_trips_count = 0U;

    if (diag->is_tripped) {
        diag->state = ESTOP_STATE_TRIPPED;
        diag->total_trips_count = 1U;
    }
}

estop_event_t estop_diag_update(estop_diag_t *diag, uint32_t current_time_ms)
{
    if (diag == NULL || diag->read_gpio_fn == NULL) {
        return ESTOP_EVENT_NONE;
    }

    /* Зчитуємо поточний рівень від опторозв'язки (true = розмикання NC / аварія) */
    bool current_raw_level = diag->read_gpio_fn();
    estop_event_t event = ESTOP_EVENT_NONE;

    switch (diag->state) {
    case ESTOP_STATE_NORMAL:
        if (current_raw_level != diag->last_raw_level) {
            diag->last_raw_level = current_raw_level;
            diag->last_state_change_ms = current_time_ms;
            diag->state = ESTOP_STATE_DEBOUNCE;
        }
        break;

    case ESTOP_STATE_DEBOUNCE:
        /* Перевіряємо, чи сигнал стабільний протягом інтервалу дебаунсу */
        if (current_raw_level != diag->last_raw_level) {
            /* Відбувся черговий фронт брязкоту — перезапускаємо таймер */
            diag->last_raw_level = current_raw_level;
            diag->last_state_change_ms = current_time_ms;
        } else if ((current_time_ms - diag->last_state_change_ms) >= diag->debounce_delay_ms) {
            /* Рівень стабілізувався — ухвалюємо рішення про новий стан */
            if (current_raw_level) {
                diag->state = ESTOP_STATE_TRIPPED;
                diag->is_tripped = true;
                diag->total_trips_count++;
                event = ESTOP_EVENT_TRIPPED;
            } else {
                diag->state = ESTOP_STATE_NORMAL;
                if (diag->is_tripped) {
                    diag->is_tripped = false;
                    event = ESTOP_EVENT_RESET;
                }
            }
        }
        break;

    case ESTOP_STATE_TRIPPED:
        if (current_raw_level != diag->last_raw_level) {
            diag->last_raw_level = current_raw_level;
            diag->last_state_change_ms = current_time_ms;
            diag->state = ESTOP_STATE_DEBOUNCE;
        }
        break;

    default:
        diag->state = ESTOP_STATE_NORMAL;
        break;
    }

    return event;
}

bool estop_diag_is_tripped(const estop_diag_t *diag)
{
    if (diag == NULL) {
        return true; /* Забезпечуємо безпечний стан за замовчуванням */
    }
    return diag->is_tripped;
}
