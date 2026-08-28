namespace Health {

struct SpiDiagnostics {
    uint32_t crc_errors{0};
    uint32_t overrun_errors{0};
    uint32_t mode_fault_errors{0};
    bool     continuous_dead_data{false};

    [[nodiscard]] constexpr uint16_t evaluate() const noexcept {
        if (mode_fault_errors > 0 || continuous_dead_data) {
            return 100;
        }

        const uint32_t total_err = crc_errors + overrun_errors;
        if (total_err == 0) {
            return 1000;
        }
        if (total_err >= 20) {
            return 300;
        }

        return static_cast<uint16_t>(1000 - (total_err * 700) / 20);
    }
};

} // namespace Health
