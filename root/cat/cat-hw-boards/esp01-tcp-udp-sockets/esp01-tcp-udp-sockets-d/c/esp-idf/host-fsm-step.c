#include <stdint.h>
#include <stdbool.h>

typedef enum {
    HOST_STATE_INIT,
    HOST_STATE_CONNECTING,
    HOST_STATE_IDLE,
    HOST_STATE_SENDING,
    HOST_STATE_RECONNECT
} host_fsm_state_t;

typedef struct {
    host_fsm_state_t state;
    uint32_t last_state_change_ms;
    uint32_t backoff_delay_ms;
    uint8_t retry_count;
} host_fsm_t;

// Обробник станів FSM хост-контролера
void host_fsm_step(host_fsm_t *fsm, uint32_t current_time_ms, bool socket_closed) {
    if (socket_closed && fsm->state != HOST_STATE_RECONNECT) {
        fsm->state = HOST_STATE_RECONNECT;
        fsm->last_state_change_ms = current_time_ms;
        return;
    }

    switch (fsm->state) {
        case HOST_STATE_INIT:
            // Відправка AT та AT+CIPMUX=1...
            fsm->state = HOST_STATE_CONNECTING;
            fsm->last_state_change_ms = current_time_ms;
            break;

        case HOST_STATE_CONNECTING:
            // Очікування CONNECT з таймаутом 10 секунд
            if (current_time_ms - fsm->last_state_change_ms > 10000) {
                fsm->state = HOST_STATE_RECONNECT;
                fsm->last_state_change_ms = current_time_ms;
            }
            break;

        case HOST_STATE_RECONNECT:
            // Реалізація exponential backoff
            if (current_time_ms - fsm->last_state_change_ms >= fsm->backoff_delay_ms) {
                fsm->backoff_delay_ms = (fsm->backoff_delay_ms * 2 > 60000) ? 60000 : fsm->backoff_delay_ms * 2;
                fsm->state = HOST_STATE_INIT;
                fsm->last_state_change_ms = current_time_ms;
            }
            break;

        default:
            break;
    }
}
