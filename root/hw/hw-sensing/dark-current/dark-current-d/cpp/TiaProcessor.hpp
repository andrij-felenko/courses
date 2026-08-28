// TiaProcessor.hpp — Ідіоматична C++ реалізація фотодіодного процесора
#pragma once
#include <cmath>
#include <optional>
#include <concepts>
#include <span>

template <std::floating_point T = float>
class TransimpedanceProcessor {
public:
    struct Config {
        T feedback_resistor_ohms{1.0e6};  // 1 МОм
        T dark_current_t0_amps{10.0e-12}; // 10 пА при 25 °C
        T cal_temp_celsius{25.0};
        T temp_doubling_step_c{8.5};
        T filter_alpha{0.15};
        T adc_vref_volts{3.3};
        T sat_margin_volts{0.05};
    };

    struct Result {
        T photocurrent_amps;
        T output_voltage;
        T estimated_dark_amps;
        bool saturated;
    };

    constexpr explicit TransimpedanceProcessor(const Config& config) noexcept
        : config_(config), filtered_voltage_(0) {}

    [[nodiscard]] T estimate_dark_current(T temp_celsius) const noexcept {
        const T delta_t = temp_celsius - config_.cal_temp_celsius;
        const T exponent = delta_t / config_.temp_doubling_step_c;
        return config_.dark_current_t0_amps * std::pow(static_cast<T>(2), exponent);
    }

    [[nodiscard]] std::optional<Result> process_cds(T dark_sample_v,
                                                    T light_sample_v,
                                                    T current_temp_c) noexcept {
        const T max_v = config_.adc_vref_volts - config_.sat_margin_volts;
        const bool is_sat = (light_sample_v >= max_v) || (light_sample_v <= config_.sat_margin_volts);

        T diff_v = light_sample_v - dark_sample_v;
        if (diff_v < static_cast<T>(0)) {
            diff_v = static_cast<T>(0);
        }

        // Оновлення IIR-фільтра
        filtered_voltage_ = (config_.filter_alpha * diff_v) +
                            ((static_cast<T>(1) - config_.filter_alpha) * filtered_voltage_);

        if (is_sat) {
            return std::nullopt; // Сигнал вийшов за лінійний діапазон
        }

        return Result{
            .photocurrent_amps = filtered_voltage_ / config_.feedback_resistor_ohms,
            .output_voltage = filtered_voltage_,
            .estimated_dark_amps = estimate_dark_current(current_temp_c),
            .saturated = false
        };
    }

    void reset() noexcept {
        filtered_voltage_ = static_cast<T>(0);
    }

private:
    Config config_;
    T filtered_voltage_;
};
