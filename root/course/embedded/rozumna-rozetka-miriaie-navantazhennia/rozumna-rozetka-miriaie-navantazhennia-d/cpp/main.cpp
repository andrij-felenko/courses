#include <cstdint>
#include <concepts>
#include <optional>

namespace socket {

struct Telemetry {
    float voltage_rms{0.0f};
    float current_rms{0.0f};
    float active_power{0.0f};
    float apparent_power{0.0f};
    float power_factor{1.0f};
    double energy_kwh{0.0};
};

class PowerMonitor {
public:
    constexpr explicit PowerMonitor(float max_current_limit = 16.0f) noexcept
        : max_current_{max_current_limit} {}

    [[nodiscard]] bool check_overcurrent(const Telemetry& data) const noexcept {
        return data.current_rms > max_current_;
    }

    [[nodiscard]] bool check_voltage_fault(const Telemetry& data) const noexcept {
        return (data.voltage_rms > 260.0f) || (data.voltage_rms < 175.0f);
    }

private:
    float max_current_{16.0f};
};

} // namespace socket
