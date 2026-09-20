#include "attenuator_calculator.hpp"
#include <cmath>
#include <algorithm>
#include <limits>
#include <iostream>

// Базові множники для ряду E24 (24 значення на декаду, допуск 5%)
const std::array<double, 24> AttenuatorCalculator::E24_BASE_VALUES = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};

// Базові множники для ряду E96 (96 значень на декаду, допуск 1%)
const std::array<double, 96> AttenuatorCalculator::E96_BASE_VALUES = {
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76
};

AttenuatorCalculator::AttenuatorCalculator(size_t positions, double input_impedance_ohm, double max_attenuation_db)
    : num_positions_(positions), input_impedance_(input_impedance_ohm), max_attenuation_db_(max_attenuation_db) {}

double AttenuatorCalculator::find_closest_resistor(double target_value_ohm, ResistorSeries series) {
    if (target_value_ohm <= 0.0) {
        return 0.0;
    }

    // Визначаємо декаду (степінь 10) для цільового опору
    double exponent = std::floor(std::log10(target_value_ohm));
    double scale = std::pow(10.0, exponent);
    double normalized_value = target_value_ohm / scale;

    double closest_base = 1.0;
    double min_diff = std::numeric_limits<double>::max();

    const auto& base_array = (series == ResistorSeries::E24) ? 
        std::vector<double>(E24_BASE_VALUES.begin(), E24_BASE_VALUES.end()) : 
        std::vector<double>(E96_BASE_VALUES.begin(), E96_BASE_VALUES.end());

    for (double val : base_array) {
        double diff = std::abs(val - normalized_value);
        if (diff < min_diff) {
            min_diff = diff;
            closest_base = val;
        }
    }

    // Перевірка межі між декадами (наприклад, 9.76 у E96 та 10.0 у наступній декаді)
    double value1 = closest_base * scale;
    double value2 = (base_array.front() * 10.0) * scale;
    if (std::abs(value2 - target_value_ohm) < std::abs(value1 - target_value_ohm)) {
        return value2;
    }

    return value1;
}

void AttenuatorCalculator::calculate(AttenuationScale scale) {
    steps_.clear();
    if (num_positions_ < 2) {
        return;
    }

    steps_.reserve(num_positions_);

    // Максимальна напруга сигналу на вході (для розрахунку потужності, 1.0 В RMS)
    const double input_voltage_rms = 1.0;

    for (size_t i = 0; i < num_positions_; ++i) {
        AttenuatorStep step;
        step.position = i + 1;

        // Позиція 1 відповідає мінімальному ослабленню (0 дБ)
        if (i == 0) {
            step.target_attenuation_db = 0.0;
        } else {
            if (scale == AttenuationScale::Logarithmic) {
                step.target_attenuation_db = (static_cast<double>(i) / (num_positions_ - 1)) * max_attenuation_db_;
            } else {
                double linear_ratio = 1.0 - (static_cast<double>(i) / (num_positions_ - 1)) * (1.0 - std::pow(10.0, -max_attenuation_db_ / 20.0));
                step.target_attenuation_db = -20.0 * std::log10(std::max(linear_ratio, 1e-6));
            }
        }

        // Переведення ослаблення у децибелах у коефіцієнт передачі напруги K = V_out / V_in
        step.target_voltage_ratio = std::pow(10.0, -step.target_attenuation_db / 20.0);

        // Розрахунок L-pad дільника напруги з постійним вхідним опором Z_in
        // K = R_shunt / (R_series + R_shunt)
        // Z_in = R_series + R_shunt  =>  R_shunt = Z_in * K,  R_series = Z_in * (1 - K)
        step.r_series_ideal = input_impedance_ * (1.0 - step.target_voltage_ratio);
        step.r_shunt_ideal = input_impedance_ * step.target_voltage_ratio;

        // Підбір опорів із рядів E24 та E96
        step.r_series_e24 = find_closest_resistor(step.r_series_ideal, ResistorSeries::E24);
        step.r_series_e96 = find_closest_resistor(step.r_series_ideal, ResistorSeries::E96);

        step.r_shunt_e24 = find_closest_resistor(step.r_shunt_ideal, ResistorSeries::E24);
        step.r_shunt_e96 = find_closest_resistor(step.r_shunt_ideal, ResistorSeries::E96);

        // Обчислення фактичних коефіцієнтів та ослаблення для E24
        double ratio_e24 = (step.r_series_e24 + step.r_shunt_e24 > 0.0) ? 
            (step.r_shunt_e24 / (step.r_series_e24 + step.r_shunt_e24)) : 0.0;
        step.actual_attenuation_db_e24 = (ratio_e24 > 0.0) ? (-20.0 * std::log10(ratio_e24)) : 999.0;
        step.error_db_e24 = std::abs(step.actual_attenuation_db_e24 - step.target_attenuation_db);

        // Обчислення фактичних коефіцієнтів та ослаблення для E96
        double ratio_e96 = (step.r_series_e96 + step.r_shunt_e96 > 0.0) ? 
            (step.r_shunt_e96 / (step.r_series_e96 + step.r_shunt_e96)) : 0.0;
        step.actual_attenuation_db_e96 = (ratio_e96 > 0.0) ? (-20.0 * std::log10(ratio_e96)) : 999.0;
        step.error_db_e96 = std::abs(step.actual_attenuation_db_e96 - step.target_attenuation_db);

        // Обчислення розсіюваної потужності (P = U^2 / R) в мВт
        double v_series = input_voltage_rms * (1.0 - step.target_voltage_ratio);
        double v_shunt = input_voltage_rms * step.target_voltage_ratio;

        step.power_dissipation_series_mw = (step.r_series_ideal > 0.0) ? 
            (1000.0 * v_series * v_series / step.r_series_ideal) : 0.0;
        step.power_dissipation_shunt_mw = (step.r_shunt_ideal > 0.0) ? 
            (1000.0 * v_shunt * v_shunt / step.r_shunt_ideal) : 0.0;

        steps_.push_back(step);
    }
}

const std::vector<AttenuatorStep>& AttenuatorCalculator::get_steps() const {
    return steps_;
}
