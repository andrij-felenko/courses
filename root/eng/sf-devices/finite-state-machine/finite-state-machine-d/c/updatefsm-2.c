DeviceState currentState = STATE_IDLE;
DeviceState previousState = STATE_ERROR;

void updateFsm() {
    bool stateChanged = (currentState != previousState);
    
    switch (currentState) {
        case STATE_IDLE:
            if (stateChanged) {
                turnOffLed();
            }
            
            if (isButtonPressed()) {
                playBeepSound();
                previousState = currentState;
                currentState = STATE_ACTIVE;
            }
            break;

        case STATE_ACTIVE:
            if (stateChanged) {
                turnOnLed();
                startTimer();
            }
            
            if (isTimeout()) {
                previousState = currentState;
                currentState = STATE_IDLE;
            }
            break;
            
        case STATE_ERROR:
            if (stateChanged) {
                logError();
            }
            break;
    }
    
    if (currentState != previousState && !stateChanged) {
        // Універсальна точка для вихідних дій
    }
}
