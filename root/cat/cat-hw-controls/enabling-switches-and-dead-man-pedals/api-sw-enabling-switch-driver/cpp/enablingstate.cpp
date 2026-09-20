#include <cstdint>
#include <functional>

enum class EnablingState : uint8_t {
    Released = 0,
    Enabled  = 1,
    Panic    = 2,
    Fault    = 3
};

struct EnablingConfig {
    std::function<bool()> read_ch_a;
    std::function<bool()> read_ch_b;
    uint16_t debounce_ms{10};
    uint16_t discrepancy_ms{100};
};

class EnablingDriver {
public:
    explicit EnablingDriver(EnablingConfig config) noexcept
        : config_{std::move(config)} {}

    bool init() noexcept {
        if (!config_.read_ch_a || !config_.read_ch_b) {
            return false;
        }
        prev_ch_a_ = config_.read_ch_a();
        prev_ch_b_ = config_.read_ch_b();
        return true;
    }

    [[nodiscard]] EnablingState state() const noexcept {
        return current_state_;
    }

private:
    EnablingConfig config_;
    EnablingState current_state_{EnablingState::Released};
    uint32_t discrepancy_timer_{0};
    bool prev_ch_a_{false};
    bool prev_ch_b_{false};
};
