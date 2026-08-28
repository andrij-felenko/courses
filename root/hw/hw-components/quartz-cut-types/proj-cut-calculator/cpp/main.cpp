#include <iostream>
#include <cmath>
#include <string_view>
#include <span>
#include <numbers>
#include <optional>
#include <vector>
#include <iomanip>

enum class QuartzCut {
    AtCut,
    BtCut,
    ScCut,
    TuningFork32k
};

struct QuartzSpec {
    QuartzCut cut{QuartzCut::AtCut};
    double nominal_freq_hz{16'000'000.0};
    double angle_offset_min{0.0}; /* Відхилення кута в кутових мінутах */
    double t0_deg_c{25.0};        /* Точка перегину / вершина параболи */
};

struct BvdModel {
    double fs_hz{0.0};
    double fp_hz{0.0};
    double c0_pf{0.0};
    double r1_ohm{0.0};
    double l1_h{0.0};
    double c1_ff{0.0};            /* фемтофаради (10^-15 Ф) */
    double q_factor{0.0};
    double capacitance_ratio{0.0};
};

struct OscillatorHealth {
    double drive_level_uw{0.0};
    double min_neg_resistance_ohm{0.0};
    double safety_factor{5.0};
    bool is_safe_startup{false};
};

class QuartzAnalyzer {
public:
    [[nodiscard]] static constexpr double calculate_ppm(const QuartzSpec& spec, double temp_deg_c) noexcept {
        const double dt = temp_deg_c - spec.t0_deg_c;
        
        switch (spec.cut) {
            case QuartzCut::AtCut: {
                /* Чутливість першого коефіцієнта: -0.0847 ppm / (°C · arcmin) */
                const double a1 = -0.0847 * spec.angle_offset_min;
                constexpr double a2 = -0.0004;
                constexpr double a3 = 0.000095;
                return (a1 * dt) + (a2 * dt * dt) + (a3 * dt * dt * dt);
            }
            case QuartzCut::BtCut: {
                constexpr double b2 = -0.040;
                return b2 * dt * dt;
            }
            case QuartzCut::ScCut: {
                constexpr double c1 = 0.0;
                constexpr double c2 = -0.0003;
                constexpr double c3 = 0.000075;
                return (c1 * dt) + (c2 * dt * dt) + (c3 * dt * dt * dt);
            }
            case QuartzCut::TuningFork32k: {
                constexpr double k2 = -0.035;
                return k2 * dt * dt;
            }
        }
        return 0.0;
    }

    [[nodiscard]] static std::optional<BvdModel> extract_bvd(
        double fs_hz, double fp_hz, double c0_pf, double r1_ohm) noexcept 
    {
        if (fs_hz <= 0.0 || fp_hz <= fs_hz || c0_pf <= 0.0 || r1_ohm <= 0.0) {
            return std::nullopt;
        }

        const double c0_farads = c0_pf * 1e-12;
        const double delta_f = fp_hz - fs_hz;
        const double c1_farads = 2.0 * c0_farads * (delta_f / fs_hz);
        
        const double omega_s = 2.0 * std::numbers::pi * fs_hz;
        const double l1_henry = 1.0 / (omega_s * omega_s * c1_farads);
        const double q = (omega_s * l1_henry) / r1_ohm;

        return BvdModel{
            .fs_hz = fs_hz,
            .fp_hz = fp_hz,
            .c0_pf = c0_pf,
            .r1_ohm = r1_ohm,
            .l1_h = l1_henry,
            .c1_ff = c1_farads * 1e15,
            .q_factor = q,
            .capacitance_ratio = c0_farads / c1_farads
        };
    }

    [[nodiscard]] static std::optional<OscillatorHealth> analyze_oscillator(
        double freq_hz, double c0_pf, double cl_pf, double r1_ohm, double vpp_volts) noexcept
    {
        if (freq_hz <= 0.0 || cl_pf <= 0.0 || r1_ohm <= 0.0 || vpp_volts <= 0.0) {
            return std::nullopt;
        }

        const double c_total = (c0_pf + cl_pf) * 1e-12;
        const double omega = 2.0 * std::numbers::pi * freq_hz;
        const double v_rms = vpp_volts / (2.0 * std::numbers::sqrt2);
        const double i_rms = v_rms * omega * c_total;
        const double power_watts = i_rms * i_rms * r1_ohm;

        const double max_allowed_uw = (freq_hz < 100'000.0) ? 1.0 : 100.0;
        const double power_uw = power_watts * 1e6;

        return OscillatorHealth{
            .drive_level_uw = power_uw,
            .min_neg_resistance_ohm = 5.0 * r1_ohm,
            .safety_factor = 5.0,
            .is_safe_startup = (power_uw <= max_allowed_uw)
        };
    }

    [[nodiscard]] static constexpr double rtc_daily_drift_seconds(double temp_deg_c) noexcept {
        constexpr QuartzSpec rtc_spec{
            .cut = QuartzCut::TuningFork32k,
            .nominal_freq_hz = 32768.0,
            .angle_offset_min = 0.0,
            .t0_deg_c = 25.0
        };
        const double ppm = calculate_ppm(rtc_spec, temp_deg_c);
        return (ppm * 1e-6) * 86400.0;
    }

    [[nodiscard]] static double rtc_diurnal_drift_seconds(double t_mean, double t_amplitude) noexcept {
        double total_drift = 0.0;
        constexpr int steps = 24;
        for (int h = 0; h < steps; ++h) {
            const double hour_angle = (2.0 * std::numbers::pi * static_cast<double>(h)) / 24.0;
            const double current_temp = t_mean + t_amplitude * std::sin(hour_angle);
            total_drift += rtc_daily_drift_seconds(current_temp) / 24.0;
        }
        return total_drift;
    }
};
