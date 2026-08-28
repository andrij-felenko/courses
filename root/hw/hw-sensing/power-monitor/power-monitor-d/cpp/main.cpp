#include <cstdint>
#include <cmath>

struct PowerMetrics {
    uint32_t bus_voltage_mv{0};
    int32_t current_ma{0};
    uint32_t power_mw{0};
};

class PowerScaleCalculator {
public:
    constexpr PowerScaleCalculator(double shunt_ohms, double max_current_amps)
        : shunt_ohms_{shunt_ohms},
          current_lsb_a_{max_current_amps / 32768.0},
          power_lsb_w_{25.0 * (max_current_amps / 32768.0)},
          cal_register_{static_cast<uint16_t>(0.00512 / ((max_current_amps / 32768.0) * shunt_ohms))} {}

    [[nodiscard]] constexpr uint16_t calibrationRegister() const noexcept {
        return cal_register_;
    }

    [[nodiscard]] constexpr PowerMetrics parse(uint16_t vbus_raw, int16_t curr_raw, uint16_t pwr_raw) const noexcept {
        return PowerMetrics{
            .bus_voltage_mv = static_cast<uint32_t>((vbus_raw * 1250ULL) / 1000ULL),
            .current_ma     = static_cast<int32_t>(curr_raw * current_lsb_a_ * 1000.0),
            .power_mw       = static_cast<uint32_t>(pwr_raw * power_lsb_w_ * 1000.0)
        };
    }

private:
    double shunt_ohms_;
    double current_lsb_a_;
    double power_lsb_w_;
    uint16_t cal_register_;
};
