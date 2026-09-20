bool ThumbwheelDriver::readValue(uint32_t &outValue) const {
    uint32_t total = 0;
    uint32_t multiplier = 1;

    for (uint8_t i = 0; i < config_.numDecades; ++i) {
        const auto &st = decades_[i];
        if (!st.isValid || st.debouncedCode > 9) {
            return false;
        }

        total += static_cast<uint32_t>(st.debouncedCode) * multiplier;
        multiplier *= 10;
    }

    outValue = total;
    return true;
}
