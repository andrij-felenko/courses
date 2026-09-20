void ThumbwheelDriver::scanTick() {
    for (uint8_t i = 0; i < config_.numDecades; ++i) {
        uint8_t raw = 0;
        if (config_.activeLow) {
            raw = (~raw) & 0x0F;
        } else {
            raw &= 0x0F;
        }

        auto &st = decades_[i];
        st.rawCode = raw;

        bool valid = (config_.codeType == ThumbwheelCodeType::Hexadecimal) ? 
                     (raw <= 0x0F) : (raw <= 9);
        st.isValid = valid;

        if (valid && (raw == st.candidateCode)) {
            if (st.stabilityCounter < config_.debounceTicks) {
                st.stabilityCounter++;
                if (st.stabilityCounter >= config_.debounceTicks) {
                    st.debouncedCode = raw;
                }
            }
        } else {
            st.candidateCode = valid ? raw : 0xFF;
            st.stabilityCounter = 0;
        }
    }
}
