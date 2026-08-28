// ThermalProtection.hpp — Ідіоматичний C++20 модуль моніторингу
#pragma once
#include <array>
#include <algorithm>
#include <span>
#include <cstdint>

namespace propulsion::thermal {

struct Config {
    float r_phase_20c{0.045f};         // Опір фази мотора при 20°C (Ом)
    float alpha_copper{0.00393f};       // Температурний коефіцієнт опору міді
    float c_th_wind{3.5f};              // Теплоємність міді обмотки (Дж/°C)
    float c_th_core{18.0f};             // Теплоємність статора (Дж/°C)
    float r_th_wind_core{1.2f};         // Тепловий опір обмотка-статор (°C/Вт)
    float r_th_core_air_base{4.8f};     // Тепловий опір статор-повітря (°C/Вт)
    float k_iron_loss{0.0025f};         // Коефіцієнт магнітних втрат статора

    float esc_temp_warn{95.0f};         // Початок тротлінгу ESC (°C)
    float esc_temp_crit{115.0f};        // Критична межа ESC (°C)
    float motor_temp_warn{100.0f};      // Початок тротлінгу мотора (°C)
    float motor_temp_crit{130.0f};      // Критична межа мотора (°C)
    float min_throttle_scale{0.35f};    // Мінімально допустимий газ тротлінгу
};

struct ChannelState {
    float t_wind_est{25.0f};
    float t_core_est{25.0f};
    float esc_temp_filtered{25.0f};
    float throttle_scale{1.0f};
    bool  is_overheated{false};
};

template <std::size_t NumChannels = 4>
class ThermalProtectionManager {
public:
    explicit constexpr ThermalProtectionManager(const Config& config, float ambient_c = 25.0f) noexcept
        : config_{config}, ambient_temp_c_{ambient_c} {
        for (auto& ch : channels_) {
            ch.t_wind_est = ambient_c;
            ch.t_core_est = ambient_c;
            ch.esc_temp_filtered = ambient_c;
        }
    }

    void update(std::size_t channel, float current_amps, uint32_t erpm,
                float esc_raw_temp, float dt_sec) noexcept {
        if (channel >= NumChannels || dt_sec <= 0.0f) return;

        auto& st = channels_[channel];

        // 1. Фільтрація температури ESC
        const float alpha_lpf = dt_sec / (0.5f + dt_sec);
        st.esc_temp_filtered += alpha_lpf * (esc_raw_temp - st.esc_temp_filtered);

        // 2. Тепловий спостерігач обмотки мотора
        const float r_cu = config_.r_phase_20c * (1.0f + config_.alpha_copper * (st.t_wind_est - 20.0f));
        const float p_copper = 1.5f * current_amps * current_amps * r_cu;

        const float erpm_k = static_cast<float>(erpm) * 0.001f;
        const float p_iron = config_.k_iron_loss * erpm_k * erpm_k;

        const float airflow_factor = 1.0f + 0.05f * erpm_k;
        const float r_th_air = config_.r_th_core_air_base / airflow_factor;

        const float q_wind_to_core = (st.t_wind_est - st.t_core_est) / config_.r_th_wind_core;
        const float q_core_to_air  = (st.t_core_est - ambient_temp_c_) / r_th_air;

        const float d_t_wind = (p_copper - q_wind_to_core) / config_.c_th_wind;
        const float d_t_core = (q_wind_to_core + p_iron - q_core_to_air) / config_.c_th_core;

        st.t_wind_est += d_t_wind * dt_sec;
        st.t_core_est += d_t_core * dt_sec;

        // 3. Розрахунок тротлінгу
        auto compute_scale = [this](float temp, float warn, float crit) noexcept -> float {
            if (temp <= warn) return 1.0f;
            if (temp >= crit) return config_.min_throttle_scale;
            return std::clamp(1.0f - (temp - warn) / (crit - warn),
                              config_.min_throttle_scale, 1.0f);
        };

        const float target_scale = std::min(
            compute_scale(st.esc_temp_filtered, config_.esc_temp_warn, config_.esc_temp_crit),
            compute_scale(st.t_wind_est, config_.motor_temp_warn, config_.motor_temp_crit)
        );

        // Плавний перехід (Rate Limiter 50%/с)
        const float max_slew = 0.5f * dt_sec;
        if (target_scale < st.throttle_scale) {
            st.throttle_scale = std::max(target_scale, st.throttle_scale - max_slew);
        } else {
            st.throttle_scale = std::min(target_scale, st.throttle_scale + max_slew);
        }

        st.is_overheated = (st.throttle_scale < 0.98f);
    }

    [[nodiscard]] constexpr float apply_throttle(std::size_t channel, float requested_throttle) const noexcept {
        if (channel >= NumChannels || requested_throttle <= 0.0f) return requested_throttle;
        return requested_throttle * channels_[channel].throttle_scale;
    }

    [[nodiscard]] const ChannelState& channel_state(std::size_t channel) const noexcept {
        return channels_[channel];
    }

private:
    Config config_;
    float  ambient_temp_c_{25.0f};
    std::array<ChannelState, NumChannels> channels_{};
};

} // namespace propulsion::thermal
