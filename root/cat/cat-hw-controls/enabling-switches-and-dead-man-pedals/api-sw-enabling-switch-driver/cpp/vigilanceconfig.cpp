#include <functional>

struct VigilanceConfig {
    uint32_t t_hold_ms{30000};
    uint32_t t_warn_ms{5000};
    uint32_t t_react_ms{3000};
    std::function<void()> on_warning;
    std::function<void()> on_alarm;
};

class VigilanceController {
public:
    explicit VigilanceController(VigilanceConfig config) noexcept
        : config_{std::move(config)} {}

    void process(EnablingState state, uint16_t tick_ms) noexcept {
        if (state == EnablingState::Enabled) {
            hold_timer_ += tick_ms;
            
            if (hold_timer_ >= config_.t_hold_ms && !warning_active_) {
                warning_active_ = true;
                if (config_.on_warning) config_.on_warning();
            }

            const uint32_t total_limit = config_.t_hold_ms + config_.t_warn_ms + config_.t_react_ms;
            if (hold_timer_ >= total_limit && !alarm_active_) {
                alarm_active_ = true;
                if (config_.on_alarm) config_.on_alarm();
            }
        } else {
            hold_timer_ = 0;
            warning_active_ = false;
            alarm_active_ = false;
        }
    }

private:
    VigilanceConfig config_;
    uint32_t hold_timer_{0};
    bool warning_active_{false};
    bool alarm_active_{false};
};
