/*
 * line_diagnostics.hpp - C++20 модуль діагностики синфазних перешкод та цілісності лінії
 */

#pragma once

#include <array>
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <span>
#include <expected>

namespace embedded::diagnostics {

enum class LineSafetyState : uint8_t {
    Ok = 0,
    WarningNoGround,        // Витік мережевої частоти 50 Гц (обрив PE)
    WarningHighCommonMode, // Постійний перекіс потенціалу GND
    CriticalSurgeEvent,    // Фіксація високовольтного імпульсу
    CriticalInsulationFail // Деградація опору ізоляції на PE
};

struct LineHealthMetrics {
    float v_cm_instant_volts{0.0F};
    float v_cm_dc_bias_volts{0.0F};
    float v_cm_noise_rms_volts{0.0F};
    float insulation_res_kohm{10000.0F};
    uint32_t surge_event_count{0};
    LineSafetyState state{LineSafetyState::Ok};
};

struct LineDiagConfig {
    float v_cm_warn_threshold_volts{7.0F};
    float v_cm_rms_warn_threshold_volts{12.0F};
    float r_iso_min_kohm{500.0F};
    float adc_vref_volts{3.3F};
    float divider_ratio{10.0F};
    uint16_t adc_midscale{2048}; // 12-бітний АЦП: середина 1.65 В
};

template <size_t WindowSize = 64>
class LineDiagnosticsMonitor {
public:
    explicit constexpr LineDiagnosticsMonitor(const LineDiagConfig& cfg) noexcept
        : config_(cfg) {}

    void add_sample(uint16_t adc_raw) noexcept {
        samples_[sample_idx_] = adc_raw;
        sample_idx_ = (sample_idx_ + 1U) % WindowSize;
        if (sample_count_ < WindowSize) {
            ++sample_count_;
        }
    }

    [[nodiscard]] LineHealthMetrics evaluate(float raw_r_iso_adc_volts) noexcept {
        LineHealthMetrics metrics{};
        metrics.surge_event_count = surge_counter_;

        if (sample_count_ == 0U) {
            metrics.state = LineSafetyState::Ok;
            return metrics;
        }

        // Обчислення напруг за даними вікна вибірок
        float sum_v = 0.0F;
        float sum_sq_diff = 0.0F;
        const size_t n = sample_count_;

        for (size_t i = 0; i < n; ++i) {
            const float v = convert_adc_to_vcm(samples_[i]);
            sum_v += v;
        }
        const float mean_v = sum_v / static_cast<float>(n);

        for (size_t i = 0; i < n; ++i) {
            const float v = convert_adc_to_vcm(samples_[i]);
            const float diff = v - mean_v;
            sum_sq_diff += diff * diff;
        }
        const float rms_noise = std::sqrt(sum_sq_diff / static_cast<float>(n));

        metrics.v_cm_instant_volts = convert_adc_to_vcm(samples_[(sample_idx_ + WindowSize - 1U) % WindowSize]);
        metrics.v_cm_dc_bias_volts = mean_v;
        metrics.v_cm_noise_rms_volts = rms_noise;

        // Розрахунок опору ізоляції
        metrics.insulation_res_kohm = calculate_insulation(raw_r_iso_adc_volts);

        // Класифікація стану лінії
        metrics.state = classify_state(metrics);
        current_state_ = metrics.state;

        return metrics;
    }

    void record_surge_event() noexcept {
        ++surge_counter_;
    }

    [[nodiscard]] LineSafetyState current_state() const noexcept {
        return current_state_;
    }

private:
    [[nodiscard]] constexpr float convert_adc_to_vcm(uint16_t raw) const noexcept {
        const float adc_volts = (static_cast<float>(raw) * config_.adc_vref_volts) / 4095.0F;
        // Зсув відносно віртуального нуля Vref/2
        const float bipolar_adc_v = adc_volts - (config_.adc_vref_volts * 0.5F);
        return bipolar_adc_v * config_.divider_ratio;
    }

    [[nodiscard]] float calculate_insulation(float sense_volts) const noexcept {
        if (sense_volts <= 0.01F) {
            return 10000.0F; // Високий опір (ідеальна ізоляція)
        }
        constexpr float r_shunt_kohm = 10.0F;
        constexpr float v_test_volts = 24.0F;
        const float i_leak_ma = sense_volts / r_shunt_kohm;
        if (i_leak_ma <= 0.0001F) {
            return 10000.0F;
        }
        return (v_test_volts - sense_volts) / i_leak_ma;
    }

    [[nodiscard]] LineSafetyState classify_state(const LineHealthMetrics& m) const noexcept {
        if (m.insulation_res_kohm < config_.r_iso_min_kohm) {
            return LineSafetyState::CriticalInsulationFail;
        }
        if (m.v_cm_noise_rms_volts > config_.v_cm_rms_warn_threshold_volts) {
            return LineSafetyState::WarningNoGround;
        }
        if (std::abs(m.v_cm_dc_bias_volts) > config_.v_cm_warn_threshold_volts) {
            return LineSafetyState::WarningHighCommonMode;
        }
        return LineSafetyState::Ok;
    }

    LineDiagConfig config_;
    std::array<uint16_t, WindowSize> samples_{};
    size_t sample_idx_{0};
    size_t sample_count_{0};
    uint32_t surge_counter_{0};
    LineSafetyState current_state_{LineSafetyState::Ok};
};

} // namespace embedded::diagnostics
