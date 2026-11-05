DeviceState currentState = DeviceState::Idle;
DeviceState previousState = DeviceState::Error; 

void updateFsm() {
    bool stateChanged = (currentState != previousState);
    
    switch (currentState) {
        case DeviceState::Idle:
            if (stateChanged) {
                turnOffLed();
            }
            
            if (isButtonPressed()) {
                playBeepSound();
                previousState = currentState;
                currentState = DeviceState::Active;
            }
            break;

        case DeviceState::Active:
            if (stateChanged) {
                turnOnLed();
                startTimer();
            }
            
            if (isTimeout()) {
                previousState = currentState;
                currentState = DeviceState::Idle;
            }
            break;
            
        case DeviceState::Error:
            if (stateChanged) {
                logError();
            }
            break;
    }
}
