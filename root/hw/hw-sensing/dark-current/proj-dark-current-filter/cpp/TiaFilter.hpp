// TiaFilter.hpp — Ідіоматичний C++20 модуль обробки оптичного фронтенду
#pragma once
#include <cmath>
#include <optional>
#include <concepts>
#include <span>

template <std::floating_point FloatT = float>
class PhotodiodeFrontEndProcessor {
public:
    struct Config {
        FloatT rf_ohms{1.0e6f};             // Опір зворотного зв'язку Rf = 1 МОм
        FloatT base_dark_current_a{10.0e-12f};// Базовий темновий струм 10 пА при 25 °C
        FloatT t0_celsius{25.0f};           // Температура калібрування
        FloatT temp_doubling_celsius{8.5f}; // Крок подвоєння темнового струму
        FloatT ema_alpha{0.15f};            // Коефіцієнт експоненційного згладжування
        FloatT v_adc_ref{3.3f};             // Опорна напруга АЦП
        FloatT v_sat_margin{0.05f};         // Межа насичення виходу ОП
    };

    struct Measurement {
        FloatT photocurrent_amperes;
        FloatT clean_voltage;
        FloatT estimated_dark_amperes;
        bool saturated;
    };

    constexpr explicit PhotodiodeFrontEndProcessor(const Config& config) noexcept
        : cfg_(config), filtered_voltage_(0) {}

    [[nodiscard]] FloatT estimate_dark_current(FloatT temp_celsius) const noexcept {
        const FloatT delta_t = temp_celsius - cfg_.t0_celsius;
        const FloatT exponent = delta_t / cfg_.temp_doubling_celsius;
        return cfg_.base_dark_current_a * std::pow(static_cast<FloatT>(2), exponent);
    }

    [[nodiscard]] std::optional<Measurement> process_sample(FloatT dark_sample_v,
                                                            FloatT light_sample_v,
                                                            FloatT current_temp_c) noexcept {
        const FloatT max_linear_v = cfg_.v_adc_ref - cfg_.v_sat_margin;
        const bool saturated = (light_sample_v >= max_linear_v) ||
                               (light_sample_v <= cfg_.v_sat_margin);

        FloatT delta_v = light_sample_v - dark_sample_v;
        if (delta_v < static_cast<FloatT>(0)) {
            delta_v = static_cast<FloatT>(0);
        }

        // Експоненційне згладжування (EMA)
        filtered_voltage_ = (cfg_.ema_alpha * delta_v) +
                            ((static_cast<FloatT>(1) - cfg_.ema_alpha) * filtered_voltage_);

        if (saturated) {
            return std::nullopt; // Каскад перевантажений, дані нелінійні
        }

        return Measurement{
            .photocurrent_amperes = filtered_voltage_ / cfg_.rf_ohms,
            .clean_voltage = filtered_voltage_,
            .estimated_dark_amperes = estimate_dark_current(current_temp_c),
            .saturated = false
        };
    }

    void reset() noexcept {
        filtered_voltage_ = static_cast<FloatT>(0);
    }

private:
    Config cfg_;
    FloatT filtered_voltage_;
};
