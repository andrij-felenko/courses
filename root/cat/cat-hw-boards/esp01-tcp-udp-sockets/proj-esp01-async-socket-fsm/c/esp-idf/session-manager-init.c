#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    DRIVER_STATE_INIT_AT,
    DRIVER_STATE_CHECK_WIFI,
    DRIVER_STATE_CONNECT_SOCKET,
    DRIVER_STATE_CONNECTED,
    DRIVER_STATE_RECOVER_SOFT,
    DRIVER_STATE_RECOVER_HARD
} driver_state_t;

typedef struct {
    driver_state_t state;
    uint32_t last_activity_ms;
    uint8_t retry_count;
} session_manager_t;

void session_manager_init(session_manager_t *sm, uint32_t current_ms) {
    sm->state = DRIVER_STATE_INIT_AT;
    sm->last_activity_ms = current_ms;
    sm->retry_count = 0;
}

void session_manager_poll(session_manager_t *sm, uint32_t current_ms, void (*hardware_reset_pin)(bool active)) {
    uint32_t elapsed = current_ms - sm->last_activity_ms;

    switch (sm->state) {
        case DRIVER_STATE_CONNECTED:
            if (elapsed > 15000) {
                sm->state = DRIVER_STATE_RECOVER_SOFT;
                sm->last_activity_ms = current_ms;
            }
            break;

        case DRIVER_STATE_RECOVER_SOFT:
            if (elapsed > 3000) {
                sm->state = DRIVER_STATE_RECOVER_HARD;
                sm->last_activity_ms = current_ms;
                sm->retry_count++;
                if (hardware_reset_pin) {
                    hardware_reset_pin(true);
                }
            }
            break;

        case DRIVER_STATE_RECOVER_HARD:
            if (elapsed > 100) {
                if (hardware_reset_pin) {
                    hardware_reset_pin(false);
                }
            }
            if (elapsed > 2000) {
                sm->state = DRIVER_STATE_INIT_AT;
                sm->last_activity_ms = current_ms;
            }
            break;

        default:
            break;
    }
}

void session_manager_on_async_event(session_manager_t *sm, const char *event_str, uint32_t current_ms) {
    sm->last_activity_ms = current_ms;
    if (sm->state == DRIVER_STATE_CONNECTED) {
        if (strstr(event_str, "CLOSED") || strstr(event_str, "WIFI DISCONNECT")) {
            sm->state = DRIVER_STATE_CONNECT_SOCKET;
        }
    }
}
