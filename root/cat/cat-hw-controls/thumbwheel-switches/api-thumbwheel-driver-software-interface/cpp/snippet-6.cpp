void ThumbwheelDriver::filterProcess(uint16_t rawFrame) {
    constexpr uint8_t DebounceThreshold = 3;
    
    for (uint8_t i = 0; i < config_.decadesCount; ++i) {
        uint8_t currentNibble = (rawFrame >> (i * 4)) & 0x0F;
        
        if (currentNibble == prevNibbles_[i]) {
            if (debounceCnt_[i] < DebounceThreshold) {
                debounceCnt_[i]++;
                if (debounceCnt_[i] == DebounceThreshold) {
                    nibbles_[i] = currentNibble;
                }
            }
        } else {
            prevNibbles_[i] = currentNibble;
            debounceCnt_[i] = 0;
        }
    }
}
