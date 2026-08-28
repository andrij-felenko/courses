namespace Health {

struct CanMonitorState {
    uint8_t  tec{0};
    uint8_t  rec{0};
    bool     is_bus_off{false};
    bool     is_passive{false};
    uint32_t recovery_timer_ms{0};
    uint32_t backoff_delay_ms{100};

    [[nodiscard]] uint16_t evaluate(uint32_t dt_ms) noexcept {
        if (is_bus_off) {
            recovery_timer_ms += dt_ms;
            if (recovery_timer_ms >= backoff_delay_ms) {
                recovery_timer_ms = 0;
                if (backoff_delay_ms < 5000) {
                    backoff_delay_ms *= 2;
                }
            }
            return 0;
        }

        backoff_delay_ms = 100;
        recovery_timer_ms = 0;

        const uint8_t max_err = std::max(tec, rec);
        if (max_err < 32) {
            return 1000;
        }
        if (max_err >= 128) {
            return 200;
        }

        return static_cast<uint16_t>(1000 - (static_cast<uint32_t>(max_err - 32) * 800) / (128 - 32));
    }
};

} // namespace Health
