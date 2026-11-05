enum class State { Idle, Walk };
State currentState = State::Idle;

void updateFsm(bool inputSignal) {
    switch(currentState) {
        case State::Idle:
            if (inputSignal) {
                currentState = State::Walk;
            }
            break;
        case State::Walk:
            if (!inputSignal) {
                currentState = State::Idle;
            }
            break;
    }
}
