#ifndef POWER_MONITOR_HPP
#define POWER_MONITOR_HPP

#include <cstdint>
#include <algorithm>
#include "water_flow_sensor.hpp"

class PowerMonitor {
public:
    explicit PowerMonitor(uint8_t adc_pin, float v_ref = 3.3f, float divider_ratio = 2.0f)
        : adc_pin_(adc_pin), v_ref_(v_ref), divider_ratio_(divider_ratio) {}

    void begin() {
        last_check_ms_ = 0;
        update(0);
    }

    // Неблокуюче вимірювання напруги живлення в головному циклі
    void update(uint32_t current_time_ms) {
        if (current_time_ms - last_check_ms_ < 3000 && last_check_ms_ != 0) {
            return;
        }

        current_voltage_ = read_raw_voltage();

        // Розрахунок стану батареї за напругою
        if (current_voltage_ < 3.4f) {
            power_state_ = PowerState::Critical;
        } else if (current_voltage_ < 3.6f) {
            power_state_ = PowerState::LowPower;
        } else {
            power_state_ = PowerState::Normal;
        }

        last_check_ms_ = current_time_ms;
    }

    float get_voltage() const { return current_voltage_; }
    PowerState get_power_state() const { return power_state_; }
    bool is_low_power_mode() const { return power_state_ != PowerState::Normal; }

private:
    uint8_t adc_pin_;
    float v_ref_;
    float divider_ratio_;

    float current_voltage_{4.1f};
    PowerState power_state_{PowerState::Normal};
    uint32_t last_check_ms_{0};

    float read_raw_voltage() {
        // Симуляція зчитування напруги АЦП (аналог analogRead у вбудованих системах)
        static float simulated_v = 4.10f;
        simulated_v -= 0.02f;
        if (simulated_v < 3.3f) simulated_v = 4.15f;
        return simulated_v;
    }
};

#endif // POWER_MONITOR_HPP
