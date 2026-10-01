typedef enum {
    HOST_STATE_IDLE,
    HOST_STATE_CONNECTING,
    HOST_STATE_CONNECTED,
    HOST_STATE_SENDING,
    HOST_STATE_ERROR_RECOVERY
} host_fsm_state_t;

void host_fsm_process(host_fsm_state_t *state, const char *rx_buf) {
    switch (*state) {
        case HOST_STATE_IDLE:
            break;
        case HOST_STATE_CONNECTING:
            if (strstr(rx_buf, "CONNECT")) {
                *state = HOST_STATE_CONNECTED;
            } else if (strstr(rx_buf, "ERROR")) {
                *state = HOST_STATE_ERROR_RECOVERY;
            }
            break;
        case HOST_STATE_CONNECTED:
            if (strstr(rx_buf, "CLOSED")) {
                *state = HOST_STATE_ERROR_RECOVERY;
            }
            break;
        case HOST_STATE_SENDING:
            break;
        case HOST_STATE_ERROR_RECOVERY:
            *state = HOST_STATE_CONNECTING;
            break;
    }
}
