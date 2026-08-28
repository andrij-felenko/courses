// esd_calc.hpp — Сучасний C++20 інтерфейс інженерного розрахунку захисту від ESD
#pragma once

#include <cmath>
#include <concepts>
#include <cstdint>
#include <expected>
#include <numbers>
#include <span>
#include <string_view>

namespace esd_design {

enum class TestLevel : uint8_t {
    Level1_2kV = 0,
    Level2_4kV,
    Level3_6kV,
    Level4_8kV,
    Custom
};

enum class AnalysisError : uint8_t {
    InvalidGeometry,
    InvalidTvsParameters,
    InvalidIcParameters,
    CalculationDivergence
};

struct PcbTraceConfig {
    double trace_len_mm{5.0};
    double trace_width_mm{0.3};
    double cu_thickness_um{35.0};
    double dielectric_h_mm{0.2};
    double stub_len_mm{0.0};       // 0.0 мм = пряме прохідне трасування
    double stub_width_mm{0.3};
    double via_height_mm{1.6};
    double via_diameter_mm{0.3};
    double via_pitch_mm{1.0};
    uint32_t via_count{4};
};

struct TvsDiodeConfig {
    double v_breakdown{6.8};       // В
    double r_dynamic{0.25};        // Ом
    double c_io_pf{0.35};          // пФ
    double l_package_nh{0.3};      // нГн
    double v_standoff{5.0};        // В
    double p_ppm_watts{150.0};     // Вт
};

struct ProtectedIcConfig {
    double v_supply{3.3};          // В
    double v_abs_max{4.0};         // В
    double i_internal_max_ma{10.0};// мА
    double r_internal_dyn{3.0};    // Ом
    double c_pin_pf{3.0};          // пФ
    double r_series_ohms{22.0};    // Ом
};

struct EsdAnalysisResult {
    double peak_current_a{0.0};
    double max_di_dt_a_per_ns{0.0};
    double l_stub_nh{0.0};
    double l_gnd_array_nh{0.0};
    double l_total_parasitic_nh{0.0};
    double v_inductive_overshoot{0.0};
    double v_tvs_clamped_peak{0.0};
    double v_ic_pin_peak{0.0};
    double i_internal_diode_ma{0.0};
    double r_series_recommended{0.0};
    double cutoff_freq_mhz{0.0};
    bool   is_safe_voltage{false};
    bool   is_safe_current{false};
    bool   is_design_passed{false};

    [[nodiscard]] constexpr bool is_acceptable() const noexcept {
        return is_design_passed;
    }
};

class EsdProtectionEngine {
public:
    // Розрахунок форми струму IEC 61000-4-2 у часі t (нс)
    [[nodiscard]] static constexpr double calculate_current_at(TestLevel level,
                                                               double custom_kv,
                                                               double t_ns) noexcept {
        if (t_ns <= 0.0) return 0.0;

        const double kv = [level, custom_kv]() noexcept {
            switch (level) {
                case TestLevel::Level1_2kV: return 2.0;
                case TestLevel::Level2_4kV: return 4.0;
                case TestLevel::Level3_6kV: return 6.0;
                case TestLevel::Level4_8kV: return 8.0;
                case TestLevel::Custom:     return custom_kv;
            }
            return 8.0;
        }();

        const double scale = kv / 8.0;
        const double ip1 = 34.0 * scale;
        const double ip2 = 14.5 * scale;
        constexpr double tau1 = 0.8;
        constexpr double tau2 = 2.2;
        constexpr double tau3 = 12.0;
        constexpr double tau4 = 45.0;
        constexpr double n = 1.8;
        constexpr double k1 = 0.92;
        constexpr double k2 = 0.88;

        const double t_tau1_n = std::pow(t_ns / tau1, n);
        const double i1 = (ip1 / k1) * (t_tau1_n / (1.0 + t_tau1_n)) * std::exp(-t_ns / tau2);

        const double t_tau3_n = std::pow(t_ns / tau3, n);
        const double i2 = (ip2 / k2) * (t_tau3_n / (1.0 + t_tau3_n)) * std::exp(-t_ns / tau4);

        return i1 + i2;
    }

    // Розрахунок індуктивності прямокутної мікросмужки (нГн)
    [[nodiscard]] static double calculate_trace_inductance(double len_mm,
                                                           double width_mm,
                                                           double thickness_um) noexcept {
        if (len_mm <= 0.0 || width_mm <= 0.0) return 0.0;
        const double t_mm = thickness_um / 1000.0;
        const double w_plus_t = width_mm + t_mm;
        return 0.2 * len_mm * (std::log(2.0 * len_mm / w_plus_t) + 0.2235 * (w_plus_t / len_mm) + 0.5);
    }

    // Розрахунок індуктивності масиву перехідних отворів (нГн)
    [[nodiscard]] static double calculate_via_array_inductance(double h_mm,
                                                               double d_mm,
                                                               double pitch_mm,
                                                               uint32_t count) noexcept {
        if (h_mm <= 0.0 || d_mm <= 0.0 || count == 0) return 0.0;
        const double l_single = 0.2 * h_mm * (std::log(4.0 * h_mm / d_mm) + 1.0);
        if (count == 1) return l_single;

        const double s_ratio = h_mm / pitch_mm;
        const double m_via = 0.2 * h_mm * (std::log(s_ratio + std::sqrt(1.0 + s_ratio * s_ratio))
                             - std::sqrt(1.0 + 1.0 / (s_ratio * s_ratio)) + 1.0 / s_ratio);

        const double n_val = static_cast<double>(count);
        return (l_single + (n_val - 1.0) * m_via) / n_val;
    }

    // Головна функція комплексного аналізу ESD-тракту
    [[nodiscard]] static std::expected<EsdAnalysisResult, AnalysisError>
    analyze(TestLevel level,
            double custom_kv,
            const PcbTraceConfig& trace,
            const TvsDiodeConfig& tvs,
            const ProtectedIcConfig& ic) noexcept {

        if (trace.via_count == 0 || trace.dielectric_h_mm <= 0.0 || tvs.v_breakdown <= 0.0) {
            return std::unexpected(AnalysisError::InvalidGeometry);
        }

        EsdAnalysisResult res{};

        const double kv = (level == TestLevel::Custom) ? custom_kv :
                          (level == TestLevel::Level1_2kV) ? 2.0 :
                          (level == TestLevel::Level2_4kV) ? 4.0 :
                          (level == TestLevel::Level3_6kV) ? 6.0 : 8.0;

        res.peak_current_a = kv * 3.75;
        constexpr double t_rise_ns = 0.8;
        res.max_di_dt_a_per_ns = res.peak_current_a / t_rise_ns;

        res.l_stub_nh = calculate_trace_inductance(trace.stub_len_mm, trace.stub_width_mm, trace.cu_thickness_um);
        res.l_gnd_array_nh = calculate_via_array_inductance(trace.via_height_mm,
                                                            trace.via_diameter_mm,
                                                            trace.via_pitch_mm,
                                                            trace.via_count);
        res.l_total_parasitic_nh = res.l_stub_nh + res.l_gnd_array_nh + tvs.l_package_nh;

        res.v_inductive_overshoot = res.l_total_parasitic_nh * res.max_di_dt_a_per_ns;
        const double v_tvs_static_clamp = tvs.v_breakdown + res.peak_current_a * tvs.r_dynamic;
        res.v_tvs_clamped_peak = v_tvs_static_clamp + res.v_inductive_overshoot;

        constexpr double v_diode_drop = 0.7;
        const double v_internal_threshold = ic.v_supply + v_diode_drop;

        if (res.v_tvs_clamped_peak > v_internal_threshold) {
            const double r_total_path = ic.r_series_ohms + ic.r_internal_dyn;
            const double i_internal_a = (res.v_tvs_clamped_peak - v_internal_threshold) / r_total_path;
            res.i_internal_diode_ma = i_internal_a * 1000.0;
            res.v_ic_pin_peak = v_internal_threshold + i_internal_a * ic.r_internal_dyn;
        } else {
            res.i_internal_diode_ma = 0.0;
            res.v_ic_pin_peak = res.v_tvs_clamped_peak;
        }

        const double i_max_allowed_a = ic.i_internal_max_ma / 1000.0;
        if (i_max_allowed_a > 0.0 && res.v_tvs_clamped_peak > v_internal_threshold) {
            const double req_r = (res.v_tvs_clamped_peak - v_internal_threshold) / i_max_allowed_a - ic.r_internal_dyn;
            res.r_series_recommended = std::max(0.0, req_r);
        } else {
            res.r_series_recommended = 0.0;
        }

        const double c_total_pf = tvs.c_io_pf + ic.c_pin_pf;
        const double r_equiv = std::max(1.0, ic.r_series_ohms);
        res.cutoff_freq_mhz = 1.0e6 / (2.0 * std::numbers::pi * r_equiv * (c_total_pf * 1.0e-12)) / 1.0e6;

        res.is_safe_voltage = (res.v_ic_pin_peak <= ic.v_abs_max);
        res.is_safe_current = (res.i_internal_diode_ma <= ic.i_internal_max_ma);
        res.is_design_passed = (res.is_safe_voltage && res.is_safe_current);

        return res;
    }
};

} // namespace esd_design
