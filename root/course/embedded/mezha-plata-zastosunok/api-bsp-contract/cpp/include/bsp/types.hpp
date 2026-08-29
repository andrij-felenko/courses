#pragma once

#include "bsp/status.hpp"

#include <chrono>
#include <cstdint>

namespace bsp {

enum class LedId : std::uint8_t {
    SystemStatus = 0,
    Warning      = 1,
    Comms        = 2
};

enum class LedState : std::uint8_t {
    Off = 0,
    On  = 1
};

enum class PowerDomain : std::uint8_t {
    Sensors = 0,
    Radio   = 1,
    Display = 2
};

enum class SleepMode : std::uint8_t {
    Light = 0,
    Deep  = 1
};

struct BatteryMetrics {
    std::uint16_t voltage_mv{0};
    std::uint8_t  charge_percent{0};
    bool          is_charging{false};
    bool          is_critical_low{false};
};

struct EnvironmentMetrics {
    std::int16_t  temperature_centi_c{0};
    std::uint32_t pressure_pa{0};
    std::uint16_t humidity_centi_pct{0};

    /* Перетворення у float — справа застосунку, не прошивки: у BSP лишається
       фіксована кома, а ці помічники живуть у заголовку й на МК не викликаються. */
    [[nodiscard]] constexpr float temperature_celsius() const noexcept {
        return static_cast<float>(temperature_centi_c) / 100.0F;
    }

    [[nodiscard]] constexpr float humidity_percent() const noexcept {
        return static_cast<float>(humidity_centi_pct) / 100.0F;
    }

    [[nodiscard]] constexpr float pressure_hpa() const noexcept {
        return static_cast<float>(pressure_pa) / 100.0F;
    }
};

/** Порогові величини контракту (див. розділ про батарею). */
inline constexpr std::uint16_t kBatteryCriticalMv = 3000;
inline constexpr std::uint16_t kBatteryCutoffMv   = 2700;
inline constexpr auto          kSensorWarmup      = std::chrono::milliseconds{15};

} // namespace bsp
