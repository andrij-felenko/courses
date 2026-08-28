typedef enum {
    STATE_OFFLINE,
    STATE_CONNECTING,
    STATE_ONLINE,
    STATE_MEASURING,
    STATE_FAULT
} device_state_t;

typedef enum {
    EVT_TIMER_WAKE,
    EVT_NET_CONNECTED,
    EVT_NET_ERROR,
    EVT_START_POLL,
    EVT_DATA_READY,
    EVT_RESET
} device_event_t;

static device_state_t current_state = STATE_OFFLINE;

void fsm_dispatch(device_event_t evt) {
    switch (current_state) {
        case STATE_OFFLINE:
            if (evt == EVT_TIMER_WAKE) {
                modem_power_on();
                current_state = STATE_CONNECTING;
            }
            break;

        case STATE_CONNECTING:
            if (evt == EVT_NET_CONNECTED) {
                current_state = STATE_ONLINE;
            } else if (evt == EVT_NET_ERROR) {
                current_state = STATE_FAULT;
            }
            break;

        case STATE_ONLINE:
            if (evt == EVT_START_POLL) {
                sensor_trigger();
                current_state = STATE_MEASURING;
            }
            break;

        case STATE_MEASURING:
            if (evt == EVT_DATA_READY) {
                telemetry_send();
                current_state = STATE_ONLINE;
            }
            break;

        case STATE_FAULT:
            if (evt == EVT_RESET) {
                system_reboot();
            }
            break;
    }
}
