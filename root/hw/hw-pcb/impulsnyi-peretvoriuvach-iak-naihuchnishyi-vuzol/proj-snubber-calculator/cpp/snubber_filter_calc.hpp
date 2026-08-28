/* snubber_filter_calc.hpp */
#ifndef SNUBBER_FILTER_CALC_HPP
#define SNUBBER_FILTER_CALC_HPP

#include <iostream>
#include <iomanip>
#include <numbers>
#include <cmath>
#include <expected>
#include <string_view>
#include <array>
#include <algorithm>

namespace power_emc {

struct Frequency {
    double hz{0.0};
    constexpr explicit Frequency(double val) noexcept : hz(val) {}
    constexpr double to_mhz() const noexcept { return hz / 1.0e6; }
    constexpr double to_khz() const noexcept { return hz / 1.0e3; }
};

struct Capacitance {
    double f{0.0};
    constexpr explicit Capacitance(double val) noexcept : f(val) {}
    constexpr double to_pf() const noexcept { return f * 1.0e12; }
    constexpr double to_uf() const noexcept { return f * 1.0e6; }
};

struct Inductance {
    double h{0.0};
    constexpr explicit Inductance(double val) noexcept : h(val) {}
    constexpr double to_nh() const noexcept { return h * 1.0e9; }
    constexpr double to_uh() const noexcept { return h * 1.0e6; }
};

struct Resistance {
    double ohms{0.0};
    constexpr explicit Resistance(double val) noexcept : ohms(val) {}
};

struct Power {
    double watts{0.0};
    constexpr explicit Power(double val) noexcept : watts(val) {}
    constexpr double to_mw() const noexcept { return watts * 1.0e3; }
};

enum class CalcError : uint8_t {
    InvalidFrequency,
    FrequencyNotShifted,
    InvalidCapacitance,
    InvalidVoltage,
    InvalidPower,
    MiddlebrookStabilityViolation
};

constexpr std::string_view error_to_string(CalcError err) noexcept {
    switch (err) {
        case CalcError::InvalidFrequency: return "Неприпустиме значення частоти (повинно бути > 0)";
        case CalcError::FrequencyNotShifted: return "Зміщена частота f2 повинна бути строго меншою за f1";
        case CalcError::InvalidCapacitance: return "Неприпустиме значення тестової ємності";
        case CalcError::InvalidVoltage: return "Вхідна напруга повинна бути більшою за нуль";
        case CalcError::InvalidPower: return "Вихідна потужність повинна бути більшою за нуль";
        case CalcError::MiddlebrookStabilityViolation: return "Порушення критерію Міддлбрука: Z_out фільтра занадто великий";
    }
    return "Невідома помилка";
}

struct SnubberSpec {
    Frequency f1;
    Frequency f2;
    Capacitance c_test;
    double v_in_volts{0.0};
    Frequency f_sw;
    double cap_multiplier{3.0};
};

struct SnubberDesign {
    Capacitance c_par;
    Inductance l_par;
    Resistance z0;
    Resistance r_snub_ideal;
    Resistance r_snub_e24;
    Capacitance c_snub_ideal;
    Capacitance c_snub_e24;
    Power p_loss;
    double i_peak_amps{0.0};
};

struct FilterSpec {
    double v_in_min_v{0.0};
    Power p_out;
    double efficiency{0.90};
    Frequency f_sw;
    double target_attenuation_db{32.0};
    Inductance l_filter;
};

struct FilterDesign {
    Resistance r_in_converter;
    Frequency f_cutoff_ideal;
    Capacitance c_filter_ideal;
    Capacitance c_filter_e24;
    Capacitance c_damping_ideal;
    Capacitance c_damping_e12;
    Resistance r_damping_ideal;
    Resistance r_damping_e24;
    Resistance z_out_max;
    double stability_margin{0.0};
    bool is_stable{false};
};

inline constexpr std::array<double, 24> E24_TABLE = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};

inline constexpr std::array<double, 12> E12_TABLE = {
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2
};

template <size_t N>
constexpr double nearest_in_array(double val, const std::array<double, N>& arr) noexcept {
    if (val <= 0.0) return 0.0;
    const double exponent = std::floor(std::log10(val));
    const double mantissa = val / std::pow(10.0, exponent);

    double best_diff = 1.0e9;
    double best_mantissa = arr[0];

    for (double item : arr) {
        double diff = std::abs(mantissa - item);
        if (diff < best_diff) {
            best_diff = diff;
            best_mantissa = item;
        }
    }

    if (std::abs(mantissa - 10.0) < best_diff) {
        return 1.0 * std::pow(10.0, exponent + 1.0);
    }
    return best_mantissa * std::pow(10.0, exponent);
}

inline std::expected<SnubberDesign, CalcError> design_snubber(const SnubberSpec& spec) noexcept {
    if (spec.f1.hz <= 0.0 || spec.f2.hz <= 0.0) {
        return std::unexpected(CalcError::InvalidFrequency);
    }
    if (spec.f2.hz >= spec.f1.hz) {
        return std::unexpected(CalcError::FrequencyNotShifted);
    }
    if (spec.c_test.f <= 0.0) {
        return std::unexpected(CalcError::InvalidCapacitance);
    }
    if (spec.v_in_volts <= 0.0) {
        return std::unexpected(CalcError::InvalidVoltage);
    }

    const double ratio = spec.f1.hz / spec.f2.hz;
    const double c_par_val = spec.c_test.f / (ratio * ratio - 1.0);
    const double omega1 = 2.0 * std::numbers::pi * spec.f1.hz;
    const double l_par_val = 1.0 / (omega1 * omega1 * c_par_val);
    const double z0_val = std::sqrt(l_par_val / c_par_val);

    const double k_c = (spec.cap_multiplier >= 1.0) ? spec.cap_multiplier : 3.0;
    const double c_snub_val = k_c * c_par_val;
    const double r_snub_val = z0_val;

    const double r_e24 = nearest_in_array(r_snub_val, E24_TABLE);
    const double c_e24 = nearest_in_array(c_snub_val, E24_TABLE);

    const double p_loss_val = c_e24 * (spec.v_in_volts * spec.v_in_volts) * spec.f_sw.hz;
    const double i_peak_val = spec.v_in_volts / r_e24;

    return SnubberDesign{
        .c_par = Capacitance(c_par_val),
        .l_par = Inductance(l_par_val),
        .z0 = Resistance(z0_val),
        .r_snub_ideal = Resistance(r_snub_ideal),
        .r_snub_e24 = Resistance(r_e24),
        .c_snub_ideal = Capacitance(c_snub_val),
        .c_snub_e24 = Capacitance(c_e24),
        .p_loss = Power(p_loss_val),
        .i_peak_amps = i_peak_val
    };
}

inline std::expected<FilterDesign, CalcError> design_input_filter(const FilterSpec& spec) noexcept {
    if (spec.v_in_min_v <= 0.0 || spec.efficiency <= 0.0 || spec.efficiency > 1.0) {
        return std::unexpected(CalcError::InvalidVoltage);
    }
    if (spec.p_out.watts <= 0.0) {
        return std::unexpected(CalcError::InvalidPower);
    }
    if (spec.f_sw.hz <= 0.0 || spec.l_filter.h <= 0.0) {
        return std::unexpected(CalcError::InvalidFrequency);
    }

    const double r_in_conv = (spec.v_in_min_v * spec.v_in_min_v * spec.efficiency) / spec.p_out.watts;
    const double f_cutoff = spec.f_sw.hz * std::pow(10.0, -spec.target_attenuation_db / 40.0);
    const double omega_c = 2.0 * std::numbers::pi * f_cutoff;
    const double c_filter_val = 1.0 / (omega_c * omega_c * spec.l_filter.h);
    const double c_filter_e24 = nearest_in_array(c_filter_val, E24_TABLE);

    constexpr double n = 4.0;
    const double c_d_val = n * c_filter_e24;
    const double c_d_e12 = nearest_in_array(c_d_val, E12_TABLE);

    const double z_char = std::sqrt(spec.l_filter.h / c_filter_e24);
    const double q_opt = std::sqrt(((2.0 + n) * (4.0 + 3.0 * n)) / (2.0 * n * n * (4.0 + n)));
    const double r_d_val = z_char * q_opt;
    const double r_d_e24 = nearest_in_array(r_d_val, E24_TABLE);

    const double z_out_max_val = z_char * (std::sqrt(2.0 * (2.0 + n)) / n);
    const double margin = r_in_conv / z_out_max_val;
    const bool stable = (margin >= 3.0);

    return FilterDesign{
        .r_in_converter = Resistance(r_in_conv),
        .f_cutoff_ideal = Frequency(f_cutoff),
        .c_filter_ideal = Capacitance(c_filter_val),
        .c_filter_e24 = Capacitance(c_filter_e24),
        .c_damping_ideal = Capacitance(c_d_val),
        .c_damping_e12 = Capacitance(c_d_e12),
        .r_damping_ideal = Resistance(r_d_val),
        .r_damping_e24 = Resistance(r_d_e24),
        .z_out_max = Resistance(z_out_max_val),
        .stability_margin = margin,
        .is_stable = stable
    };
}

} // namespace power_emc

#endif /* SNUBBER_FILTER_CALC_HPP */
