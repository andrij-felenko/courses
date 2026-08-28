// climate_engine.hpp
// Модуль захисту оболонки та розрахунку точки роси (C++20)

#pragma once

#include <cmath>
#include <cstdint>
#include <algorithm>

namespace embedded::thermal {

enum class StatusFlags : uint8_t {
    Normal            = 0,
    CondensationRisk  = 1 << 0,
    MembraneBlocked   = 1 << 1,
    SealFailure       = 1 << 2,
    ThermalOverheat   = 1 << 3
};

constexpr StatusFlags operator|(StatusFlags a, StatusFlags b) noexcept {
    return static_cast<StatusFlags>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

constexpr bool has_flag(StatusFlags mask, StatusFlags flag) noexcept {
    return (static_cast<uint8_t>(mask) & static_cast<uint8_t>(flag)) != 0;
}

enum class PowerLevel : uint8_t {
    Full = 0,
    Throttle75,
    Throttle50,
    SafeMode
};

struct EnclosureTelemetry {
    float internal_temp_c{25.0f};
    float internal_humidity_rh{50.0f};
    float internal_pressure_kpa{101.325f};
    float chassis_temp_c{25.0f};
    float ambient_pressure_kpa{101.325f};
};

struct DiagnosisResult {
    float dew_point_c{0.0f};
    float dew_point_margin_c{100.0f};
    float delta_pressure_kpa{0.0f};
    StatusFlags flags{StatusFlags::Normal};
    PowerLevel power_level{PowerLevel::Full};
};

class ClimateEngine {
public:
    static constexpr float CriticalDewMarginC = 3.0f;
    static constexpr float BlockedMembraneThresholdKPa = 5.0f;
    static constexpr float LeakRateThresholdKPaPerSec = 0.25f;

    [[nodiscard]] DiagnosisResult evaluate(const EnclosureTelemetry& t, float prev_pressure_kpa, float dt_sec) const noexcept {
        DiagnosisResult res{};

        // 1. Обчислення точки роси
        res.dew_point_c = compute_dew_point(t.internal_temp_c, t.internal_humidity_rh);
        res.dew_point_margin_c = t.chassis_temp_c - res.dew_point_c;

        if (res.dew_point_margin_c < CriticalDewMarginC) {
            res.flags = res.flags | StatusFlags::CondensationRisk;
        }

        // 2. Аналіз блокування дихальної мембрани
        res.delta_pressure_kpa = t.internal_pressure_kpa - t.ambient_pressure_kpa;
        if (std::abs(res.delta_pressure_kpa) > BlockedMembraneThresholdKPa) {
            res.flags = res.flags | StatusFlags::MembraneBlocked;
        }

        // 3. Аналіз швидкості прориву ущільнення
        if (dt_sec > 0.01f) {
            const float dp_dt = std::abs(t.internal_pressure_kpa - prev_pressure_kpa) / dt_sec;
            if (dp_dt > LeakRateThresholdKPaPerSec) {
                res.flags = res.flags | StatusFlags::SealFailure;
            }
        }

        // 4. Автомат керування потужністю
        if (t.internal_temp_c > 85.0f || t.chassis_temp_c > 75.0f) {
            res.flags = res.flags | StatusFlags::ThermalOverheat;
            res.power_level = PowerLevel::SafeMode;
        } else if (t.internal_temp_c > 75.0f || t.chassis_temp_c > 65.0f) {
            res.power_level = PowerLevel::Throttle50;
        } else if (t.internal_temp_c > 65.0f || t.chassis_temp_c > 55.0f) {
            res.power_level = PowerLevel::Throttle75;
        } else {
            res.power_level = PowerLevel::Full;
        }

        return res;
    }

private:
    [[nodiscard]] static float compute_dew_point(float temp_c, float rh) noexcept {
        const float clamped_rh = std::clamp(rh, 0.1f, 100.0f);
        constexpr float a = 17.27f;
        constexpr float b = 237.7f;
        const float alpha = (a * temp_c) / (b + temp_c) + std::log(clamped_rh / 100.0f);
        return (b * alpha) / (a - alpha);
    }
};

} // namespace embedded::thermal
