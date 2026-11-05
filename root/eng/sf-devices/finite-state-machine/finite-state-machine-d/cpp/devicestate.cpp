enum class DeviceState {
    Idle,
    Active,
    Error
};

DeviceState currentState = DeviceState::Idle;

void updateFsm() {
    switch (currentState) {
        case DeviceState::Idle:
            if (isButtonPressed()) {
                currentState = DeviceState::Active;
            }
            break;

        case DeviceState::Active:
            if (isErrorDetected()) {
                currentState = DeviceState::Error;
            } else if (isTimeout()) {
                currentState = DeviceState::Idle;
            }
            break;

        case DeviceState::Error:
            if (isResetCommand()) {
                currentState = DeviceState::Idle;
            }
            break;
    }
}
