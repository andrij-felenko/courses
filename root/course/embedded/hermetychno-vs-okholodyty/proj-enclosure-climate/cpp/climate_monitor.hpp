// climate_monitor.hpp
// Модуль контролю мікроклімату герметичного корпусу (C++20)

#pragma once

#include <cmath>
#include <cstdint>
#include <array>
#include <optional>
#include <span>

namespace embedded::enclosure {

enum class ClimateWarning : uint8_t {
    None              = 0,
    CondensationRisk  = 1 << 0,
    MembraneClogged   = 1 << 1,
    SealBreach        = 1 << 2,
    Overheat          = 1 << 3
};

constexpr ClimateWarning operator|(ClimateWarning lhs, ClimateWarning rhs) noexcept {
    return static_cast<ClimateWarning>(static_cast<uint8_t>(lhs) | static_cast<uint8_t>(rhs));
}

constexpr bool has_flag(ClimateWarning val, ClimateWarning flag) noexcept {
    return (static_cast<uint8_t>(val) & static_cast<uint8_t>(flag)) != 0;
}

enum class ThrottleLevel : uint8_t {
    None = 0,
    Light,      // -25% тактової частоти
    Heavy,      // -50% частоти, вимкнення радіо
    Critical    // Перехід у режим глибокого сну
};

struct SensorReadings {
    float internal_temp_c{25.0f};
    float relative_humidity{50.0f};
    float internal_pressure_kpa{101.325f};
    float wall_temp_c{25.0f};
    float ambient_pressure_kpa{101.325f};
};

struct EnclosureState {
    float dew_point_c{0.0f};
    float dew_margin_c{100.0f};
    float pressure_delta_kpa{0.0f};
    float dp_dt_kpa_s{0.0f};
    ClimateWarning warnings{ClimateWarning::None};
    ThrottleLevel throttle{ThrottleLevel::None};
};

template <size_t HistorySize = 8>
class ClimateMonitor {
public:
    static constexpr float DewMarginThresholdC = 3.0f;
    static constexpr float LeakRateThresholdKPaS = 0.25f;
    static constexpr float MembraneClogThresholdKPa = 5.0f;

    constexpr ClimateMonitor() noexcept = default;

    EnclosureState update(const SensorReadings& raw, uint32_t now_ms) noexcept {
        const float dew_point = compute_dew_point(raw.internal_temp_c, raw.relative_humidity);
        const float dew_margin = raw.wall_temp_c - dew_point;
        const float delta_p = raw.internal_pressure_kpa - raw.ambient_pressure_kpa;

        float dp_dt = 0.0f;
        if (history_count_ > 0) {
            const size_t oldest_idx = (history_count_ < HistorySize) ? 0 : history_idx_;
            const float dt_sec = static_cast<float>(now_ms - timestamp_history_[oldest_idx]) / 1000.0f;
            if (dt_sec > 0.05f) {
                const float dp = raw.internal_pressure_kpa - pressure_history_[oldest_idx];
                dp_dt = dp / dt_sec;
            }
        }

        pressure_history_[history_idx_] = raw.internal_pressure_kpa;
        timestamp_history_[history_idx_] = now_ms;
        history_idx_ = (history_idx_ + 1) % HistorySize;
        if (history_count_ < HistorySize) {
            ++history_count_;
        }

        ClimateWarning warnings = ClimateWarning::None;
        if (dew_margin < DewMarginThresholdC) {
            warnings = warnings | ClimateWarning::CondensationRisk;
        }
        if (std::abs(delta_p) > MembraneClogThresholdKPa) {
            warnings = warnings | ClimateWarning::MembraneClogged;
        }
        if (std::abs(dp_dt) > LeakRateThresholdKPaS) {
            warnings = warnings | ClimateWarning::SealBreach;
        }
        if (raw.internal_temp_c > 85.0f || raw.wall_temp_c > 75.0f) {
            warnings = warnings | ClimateWarning::Overheat;
        }

        ThrottleLevel throttle = ThrottleLevel::None;
        if (raw.internal_temp_c > 95.0f || raw.wall_temp_c > 85.0f) {
            throttle = ThrottleLevel::Critical;
        } else if (raw.internal_temp_c > 85.0f || raw.wall_temp_c > 75.0f) {
            throttle = ThrottleLevel::Heavy;
        } else if (raw.internal_temp_c > 75.0f || raw.wall_temp_c > 65.0f) {
            throttle = ThrottleLevel::Light;
        }

        current_state_ = EnclosureState{
            .dew_point_c = dew_point,
            .dew_margin_c = dew_margin,
            .pressure_delta_kpa = delta_p,
            .dp_dt_kpa_s = dp_dt,
            .warnings = warnings,
            .throttle = throttle
        };

        return current_state_;
    }

    [[nodiscard]] const EnclosureState& state() const noexcept {
        return current_state_;
    }

private:
    static float compute_dew_point(float temp_c, float rh) noexcept {
        const float clamped_rh = std::clamp(rh, 0.01f, 100.0f);
        constexpr float a = 17.27f;
        constexpr float b = 237.7f;
        const float gamma = (a * temp_c) / (b + temp_c) + std::log(clamped_rh / 100.0f);
        return (b * gamma) / (a - gamma);
    }

    std::array<float, HistorySize> pressure_history_{};
    std::array<uint32_t, HistorySize> timestamp_history_{};
    size_t history_idx_{0};
    size_t history_count_{0};
    EnclosureState current_state_{};
};

} // namespace embedded::enclosure
