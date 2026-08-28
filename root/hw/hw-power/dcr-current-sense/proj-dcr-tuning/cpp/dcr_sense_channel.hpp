// dcr_sense_channel.hpp - Об'єктно-орієнтований канал DCR-сенсингу (C++20)
#pragma once

#include <cstdint>
#include <algorithm>
#include <concepts>
#include <array>
#include <memory>

class DcrSenseChannel {
public:
    struct Config {
        float dcr_25c_ohm{0.00032f};       // DCR котушки при 25 °C (наприклад 0.32 мОм)
        float amp_gain{20.0f};              // Підсилення диференційного підсилювача
        float vref_v{3.300f};               // Опорна напруга АЦП (В)
        uint32_t adc_max_counts{4096};      // Роздільність АЦП (12 біт)
        float isat_threshold_a{45.0f};      // Струм початку нелінійності осердя (А)
        float sat_correction_factor{0.02f}; // Коефіцієнт спаду L(I)
    };

    explicit constexpr DcrSenseChannel(const Config& cfg) noexcept
        : config_(cfg), effective_dcr_(cfg.dcr_25c_ohm) {}

    // Автокалібрування апаратного зміщення нуля
    constexpr void calibrate_zero_offset(uint16_t raw_zero_adc) noexcept {
        zero_offset_counts_ = static_cast<int32_t>(raw_zero_adc);
    }

    // Оновлення поточної температури кристала котушки
    void update_temperature(float temp_celsius) noexcept {
        current_temp_c_ = temp_celsius;
        constexpr float tcr_copper = 0.00393f;
        effective_dcr_ = config_.dcr_25c_ohm * (1.0f + tcr_copper * (temp_celsius - 25.0f));
    }

    // Миттєвий розрахунок струму за відліком АЦП (викликається в ISR)
    [[nodiscard]] float process_sample(uint16_t raw_adc) noexcept {
        const int32_t net_counts = static_cast<int32_t>(raw_adc) - zero_offset_counts_;
        if (net_counts <= 0) {
            last_current_a_ = 0.0f;
            return 0.0f;
        }

        // Переведення відліків АЦП у фізичну напругу на конденсаторі C_s
        const float v_adc = (static_cast<float>(net_counts) / static_cast<float>(config_.adc_max_counts)) * config_.vref_v;
        const float v_cs = v_adc / config_.amp_gain;

        // Розрахунок струму з компенсацією нагріву DCR(T)
        float current = v_cs / effective_dcr_;

        // Нелінійна поліноміальна поправка на спад індуктивності L(I)
        if (current > config_.isat_threshold_a) {
            const float delta_i = current - config_.isat_threshold_a;
            current -= delta_i * delta_i * config_.sat_correction_factor;
        }

        last_current_a_ = current;
        return current;
    }

    [[nodiscard]] constexpr float get_last_current() const noexcept { return last_current_a_; }
    [[nodiscard]] constexpr float get_effective_dcr() const noexcept { return effective_dcr_; }
    [[nodiscard]] constexpr float get_temperature() const noexcept { return current_temp_c_; }

private:
    Config config_{};
    int32_t zero_offset_counts_{0};
    float current_temp_c_{25.0f};
    float effective_dcr_{0.00032f};
    float last_current_a_{0.0f};
};
