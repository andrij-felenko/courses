typedef enum {
    STATE_IDLE,
    STATE_ACTIVE,
    STATE_ERROR
} DeviceState;

DeviceState currentState = STATE_IDLE;

void updateFsm() {
    switch (currentState) {
        case STATE_IDLE:
            if (isButtonPressed()) {
                currentState = STATE_ACTIVE;
            }
            break;

        case STATE_ACTIVE:
            if (isErrorDetected()) {
                currentState = STATE_ERROR;
            } else if (isTimeout()) {
                currentState = STATE_IDLE;
            }
            break;

        case STATE_ERROR:
            if (isResetCommand()) {
                currentState = STATE_IDLE;
            }
            break;
    }
}
