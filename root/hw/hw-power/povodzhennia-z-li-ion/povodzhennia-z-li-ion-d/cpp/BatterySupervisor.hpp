// BatterySupervisor.hpp — Ідіоматичний модуль контролю безпеки на C++20
#pragma once
#include <cstdint>
#include <expected>

namespace BatteryManagement {

enum class SafetyError : uint8_t {
    None = 0,
    OverVoltage,
    DeepOverDischarge,
    ColdPlatingHazard,
    OverTemperature
};

struct BatteryTelemetry {
    uint16_t cell_voltage_mv;
    int16_t  temperature_c;
    int16_t  current_ma;
};

struct TargetChargeProfile {
    bool allow_charge{false};
    uint16_t max_voltage_mv{4200};
    uint16_t max_current_ma{0};
};

class BatterySupervisor {
public:
    [[nodiscard]] static constexpr std::expected<TargetChargeProfile, SafetyError>
    evaluate_policy(const BatteryTelemetry& telem) noexcept {
        // 1. Захист від розчинення міді при перерозряді нижче 2.0 В
        if (telem.cell_voltage_mv < 2000) {
            return std::unexpected(SafetyError::DeepOverDischarge);
        }

        // 2. Захист від перезаряду
        if (telem.cell_voltage_mv > 4250) {
            return std::unexpected(SafetyError::OverVoltage);
        }

        // 3. JEITA температурне профілювання
        if (telem.temperature_c < 0) {
            return std::unexpected(SafetyError::ColdPlatingHazard);
        }

        if (telem.temperature_c >= 60) {
            return std::unexpected(SafetyError::OverTemperature);
        }

        TargetChargeProfile profile{};
        profile.allow_charge = true;

        if (telem.temperature_c < 10) {
            profile.max_current_ma = 500;  // 0.2C..0.5C на холоді
            profile.max_voltage_mv = 4200;
        } else if (telem.temperature_c <= 45) {
            profile.max_current_ma = 2000; // 1.0C номінал
            profile.max_voltage_mv = 4200;
        } else {
            // 45..60 °C — знижена напруга для захисту електроліту
            profile.max_current_ma = 1000;
            profile.max_voltage_mv = 4100;
        }

        return profile;
    }
};

} // namespace BatteryManagement
