#include <cstdint>
#include <chrono>

class SensorPowerGuard {
public:
    using Clock = std::chrono::steady_clock;

    void start_power_timer() {
        hw_power_rail_enable(true);
        power_on_time_ = Clock::now();
        power_stable_ = false;
    }

    [[nodiscard]] bool is_power_ready(std::chrono::milliseconds required_boot_time) {
        if (power_stable_) {
            return true;
        }
        if (Clock::now() - power_on_time_ >= required_boot_time) {
            power_stable_ = true;
            return true;
        }
        return false;
    }

private:
    Clock::time_point power_on_time_{};
    bool power_stable_{false};
};
