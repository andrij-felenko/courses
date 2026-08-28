#ifndef BSP_TYPES_HPP
#define BSP_TYPES_HPP

#include "bsp_status.hpp"
#include <cstdint>

namespace bsp {

enum class LedId : uint8_t {
    SystemStatus = 0,
    Warning      = 1,
    Comms        = 2
};

enum class LedState : uint8_t {
    Off = 0,
    On  = 1
};

enum class PowerDomain : uint8_t {
    Sensors = 0,
    Radio   = 1,
    Display = 2
};

enum class SleepMode : uint8_t {
    Light = 0,
    Deep  = 1
};

struct BatteryMetrics {
    uint16_t voltage_mv{0};
    uint8_t  charge_percent{0};
    bool     is_charging{false};
    bool     is_critical_low{false};
};

struct EnvironmentMetrics {
    int16_t  temperature_centi_c{0};
    uint32_t pressure_pa{0};
    uint16_t humidity_centi_pct{0};

    [[nodiscard]] constexpr float temperature_celsius() const noexcept {
        return static_cast<float>(temperature_centi_c) / 100.0f;
    }

    [[nodiscard]] constexpr float humidity_percent() const noexcept {
        return static_cast<float>(humidity_centi_pct) / 100.0f;
    }
};

} // namespace bsp

#endif /* BSP_TYPES_HPP */
