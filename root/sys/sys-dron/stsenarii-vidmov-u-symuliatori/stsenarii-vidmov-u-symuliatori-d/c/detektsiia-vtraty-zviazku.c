#include <stdbool.h>
#include <stdint.h>

#define LINK_TIMEOUT_US       1500000ULL  // 1.5 секунди без пакетів = аварія
#define DEBOUNCE_HOLD_US      2000000ULL  // 2.0 секунди зависання перед RTL
#define RECOVERY_WINDOW_US    1000000ULL  // 1.0 секунда стабільного зв'язку для скидання

typedef enum {
    LINK_STATE_OK = 0,
    LINK_STATE_DEBOUNCE_HOLD,
    LINK_STATE_FAILSAFE_ACTIVE
} link_failsafe_state_t;

typedef struct {
    uint64_t last_packet_time_us;
    uint64_t loss_detected_time_us;
    uint64_t recovery_start_time_us;
    link_failsafe_state_t state;
    bool failsafe_triggered;
} link_watchdog_t;

void link_watchdog_init(link_watchdog_t *wd) {
    wd->last_packet_time_us = 0;
    wd->loss_detected_time_us = 0;
    wd->recovery_start_time_us = 0;
    wd->state = LINK_STATE_OK;
    wd->failsafe_triggered = false;
}

void link_watchdog_on_packet_received(link_watchdog_t *wd, uint64_t now_us) {
    wd->last_packet_time_us = now_us;
    if (wd->state == LINK_STATE_DEBOUNCE_HOLD) {
        if (wd->recovery_start_time_us == 0) {
            wd->recovery_start_time_us = now_us;
        } else if (now_us - wd->recovery_start_time_us >= RECOVERY_WINDOW_US) {
            wd->state = LINK_STATE_OK;
            wd->loss_detected_time_us = 0;
            wd->recovery_start_time_us = 0;
        }
    }
}

link_failsafe_state_t link_watchdog_update(link_watchdog_t *wd, uint64_t now_us) {
    uint64_t silence_duration = now_us - wd->last_packet_time_us;

    switch (wd->state) {
    case LINK_STATE_OK:
        if (silence_duration > LINK_TIMEOUT_US) {
            wd->state = LINK_STATE_DEBOUNCE_HOLD;
            wd->loss_detected_time_us = now_us;
            wd->recovery_start_time_us = 0;
        }
        break;

    case LINK_STATE_DEBOUNCE_HOLD:
        if (silence_duration <= LINK_TIMEOUT_US) {
            // Пакет прийшов, відновлення обробляється у callback
        } else if (now_us - wd->loss_detected_time_us >= DEBOUNCE_HOLD_US) {
            wd->state = LINK_STATE_FAILSAFE_ACTIVE;
            wd->failsafe_triggered = true;
        }
        break;

    case LINK_STATE_FAILSAFE_ACTIVE:
        // Вихід із активного Failsafe вимагає ручного підтвердження або тривалого лінка
        if (silence_duration <= LINK_TIMEOUT_US) {
            if (wd->recovery_start_time_us == 0) {
                wd->recovery_start_time_us = now_us;
            } else if (now_us - wd->recovery_start_time_us >= (RECOVERY_WINDOW_US * 3)) {
                wd->state = LINK_STATE_OK;
                wd->failsafe_triggered = false;
            }
        } else {
            wd->recovery_start_time_us = 0;
        }
        break;
    }

    return wd->state;
}
