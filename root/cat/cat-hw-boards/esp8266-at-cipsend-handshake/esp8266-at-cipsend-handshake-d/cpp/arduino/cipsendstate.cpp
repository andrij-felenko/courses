enum class CipsendState {
    Idle,
    WaitPrompt,
    SendingData,
    WaitResult
};

bool checkCipsendPrompt(uint8_t rxByte, CipsendState& state) {
    static uint8_t prevByte = 0;

    if (state == CipsendState::WaitPrompt) {
        if (prevByte == '>' && rxByte == ' ') {
            state = CipsendState::SendingData;
            prevByte = 0;
            return true;
        }
        prevByte = rxByte;
    }
    return false;
}
