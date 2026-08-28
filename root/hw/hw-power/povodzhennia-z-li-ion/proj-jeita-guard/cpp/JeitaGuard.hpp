// JeitaGuard.hpp — Об'єктно-орієнтований сторож безпеки заряду
#pragma once
#include <cstdint>
#include <cmath>
#include <expected>
#include <algorithm>

namespace BatterySafety {

enum class JeitaZone : uint8_t {
    Cold = 0,   // < 0 °C: Заряд заблоковано
    Cool,       // 0..10 °C: Знижений струм
    Standard,   // 10..45 °C: Номінальний режим
    Warm,       // 45..60 °C: Знижена напруга
    Hot         // >= 60 °C: Заряд заблоковано
};

enum class GuardFault : uint8_t {
    SensorFault,
    RapidThermalRise,
    HardwareTrip
};

struct ChargeLimits {
    bool enabled;
    uint16_t current_ma;
    uint16_t voltage_mv;
    JeitaZone zone;
};

struct JeitaConfig {
    float temp_cold_c{0.0f};
    float temp_cool_c{10.0f};
    float temp_warm_c{45.0f};
    float temp_hot_c{60.0f};
    float hyst_c{2.0f};
    float max_temp_rate_c_per_s{1.5f};
    uint16_t standard_current_ma{2000};
    uint16_t reduced_current_ma{500};
    uint16_t standard_voltage_mv{4200};
    uint16_t reduced_voltage_mv{4100};
};

class NtcSensor {
public:
    constexpr NtcSensor(float pullup_r, float nominal_r, float beta) noexcept
        : pullup_ohm_{pullup_r}, nominal_ohm_{nominal_r}, beta_{beta} {}

    [[nodiscard]] std::expected<float, GuardFault> read_temperature(uint16_t raw_adc, uint16_t max_adc) const noexcept {
        if (raw_adc == 0 || raw_adc >= max_adc) {
            return std::unexpected(GuardFault::SensorFault);
        }
        const float ratio = static_cast<float>(raw_adc) / static_cast<float>(max_adc);
        const float r_ntc = pullup_ohm_ * (ratio / (1.0f - ratio));
        constexpr float t0_kelvin = 298.15f;
        const float inv_t = (1.0f / t0_kelvin) + (1.0f / beta_) * std::log(r_ntc / nominal_ohm_);
        return (1.0f / inv_t) - 273.15f;
    }

private:
    float pullup_ohm_;
    float nominal_ohm_;
    float beta_;
};

class JeitaGuard {
public:
    explicit constexpr JeitaGuard(const JeitaConfig& config) noexcept
        : config_{config}, current_zone_{JeitaZone::Cold} {}

    std::expected<ChargeLimits, GuardFault> update(float current_temp_c, float dt_s) noexcept {
        if (fault_latched_) {
            return std::unexpected(GuardFault::HardwareTrip);
        }

        if (dt_s > 0.001f) {
            const float rate = (current_temp_c - last_temp_c_) / dt_s;
            if (rate > config_.max_temp_rate_c_per_s && current_temp_c > config_.temp_cool_c) {
                fault_latched_ = true;
                return std::unexpected(GuardFault::RapidThermalRise);
            }
        }
        last_temp_c_ = current_temp_c;
        evaluate_zone(current_temp_c);

        return calculate_limits();
    }

    void reset_latch() noexcept {
        fault_latched_ = false;
    }

private:
    void evaluate_zone(float temp_c) noexcept {
        switch (current_zone_) {
            case JeitaZone::Cold:
                if (temp_c >= (config_.temp_cold_c + config_.hyst_c))
                    current_zone_ = JeitaZone::Cool;
                break;
            case JeitaZone::Cool:
                if (temp_c < config_.temp_cold_c)
                    current_zone_ = JeitaZone::Cold;
                else if (temp_c >= (config_.temp_cool_c + config_.hyst_c))
                    current_zone_ = JeitaZone::Standard;
                break;
            case JeitaZone::Standard:
                if (temp_c < (config_.temp_cool_c - config_.hyst_c))
                    current_zone_ = JeitaZone::Cool;
                else if (temp_c >= config_.temp_warm_c)
                    current_zone_ = JeitaZone::Warm;
                break;
            case JeitaZone::Warm:
                if (temp_c < (config_.temp_warm_c - config_.hyst_c))
                    current_zone_ = JeitaZone::Standard;
                else if (temp_c >= config_.temp_hot_c)
                    current_zone_ = JeitaZone::Hot;
                break;
            case JeitaZone::Hot:
                if (temp_c < (config_.temp_hot_c - config_.hyst_c))
                    current_zone_ = JeitaZone::Warm;
                break;
        }
    }

    [[nodiscard]] ChargeLimits calculate_limits() const noexcept {
        ChargeLimits limits{};
        limits.zone = current_zone_;
        switch (current_zone_) {
            case JeitaZone::Cold:
            case JeitaZone::Hot:
                limits.enabled = false;
                limits.current_ma = 0;
                limits.voltage_mv = config_.standard_voltage_mv;
                break;
            case JeitaZone::Cool:
                limits.enabled = true;
                limits.current_ma = config_.reduced_current_ma;
                limits.voltage_mv = config_.standard_voltage_mv;
                break;
            case JeitaZone::Standard:
                limits.enabled = true;
                limits.current_ma = config_.standard_current_ma;
                limits.voltage_mv = config_.standard_voltage_mv;
                break;
            case JeitaZone::Warm:
                limits.enabled = true;
                limits.current_ma = config_.reduced_current_ma;
                limits.voltage_mv = config_.reduced_voltage_mv;
                break;
        }
        return limits;
    }

    JeitaConfig config_;
    JeitaZone current_zone_;
    float last_temp_c_{25.0f};
    bool fault_latched_{false};
};

} // namespace BatterySafety
