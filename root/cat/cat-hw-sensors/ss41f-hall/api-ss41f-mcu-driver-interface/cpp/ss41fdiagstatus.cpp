enum class SS41FDiagStatus {
    Ok,
    DebounceBlocked,
    Timeout,
    FrequencyOverflow
};

class SS41FDiagnostics {
public:
    static SS41FDiagStatus validateEvent(uint32_t delta_us, uint32_t min_debounce_us, uint32_t max_frequency_hz) {
        if (delta_us < min_debounce_us) {
            return SS41FDiagStatus::DebounceBlocked;
        }

        uint32_t min_period_us = 1000000 / (max_frequency_hz * 2);
        if (delta_us < min_period_us) {
            return SS41FDiagStatus::FrequencyOverflow;
        }

        return SS41FDiagStatus::Ok;
    }
};
