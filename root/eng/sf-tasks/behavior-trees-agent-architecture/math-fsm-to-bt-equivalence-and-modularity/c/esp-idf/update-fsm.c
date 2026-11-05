typedef enum { STATE_IDLE, STATE_WALK } state_t;
state_t current_state = STATE_IDLE;

void update_fsm(bool input_signal) {
    switch(current_state) {
        case STATE_IDLE:
            if (input_signal) {
                current_state = STATE_WALK;
            }
            break;
        case STATE_WALK:
            if (!input_signal) {
                current_state = STATE_IDLE;
            }
            break;
    }
}
