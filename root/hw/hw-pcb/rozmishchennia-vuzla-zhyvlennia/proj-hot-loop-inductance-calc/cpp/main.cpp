#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <format>
#include <vector>
#include <array>
#include <expected>

namespace power_pcb {

constexpr double MU_0 = 1.256637061435917295385e-6; // Гн/м

struct TraceGeometry {
    double length_mm{0.0};
    double width_mm{0.0};
    double thickness_um{35.0};
    double height_gnd_mm{0.1};
};

struct ViaArrayParams {
    double board_thickness_mm{1.6};
    double drill_diameter_mm{0.3};
    int count{1};
    double pitch_mm{1.0};
};

struct ConverterSetup {
    double v_in{24.0};
    double i_sw{15.0};
    double t_fall_ns{2.0};
    TraceGeometry top_trace;
    ViaArrayParams vias;
    double cap_esl_nh{0.35};
    double fet_pkg_nh{0.4};
    double c_oss_pf{400.0};
    double r_loop_mohm{8.0};
};

struct SimulationReport {
    double l_trace_nh{0.0};
    double m_gnd_nh{0.0};
    double l_vias_nh{0.0};
    double l_total_loop_nh{0.0};
    double v_spike_ideal{0.0};
    double v_max_transient{0.0};
    double f_ringing_mhz{0.0};
    double r_snub_opt_ohm{0.0};
    double c_snub_opt_pf{0.0};
    double p_snub_watt{0.0};
};

enum class AnalysisError {
    InvalidGeometry,
    ZeroTimeStep,
    InvalidCapacitance
};

class HotLoopSolver {
public:
    [[nodiscard]] static constexpr double calcPartialSelfInductance(double l_mm, double w_mm, double t_mm) noexcept {
        if (l_mm <= 0.0 || w_mm <= 0.0) return 0.0;
        const double l_m = l_mm * 1e-3;
        const double w_m = w_mm * 1e-3;
        const double t_m = (t_mm > 0.0) ? (t_mm * 1e-3) : 1e-6;

        const double term1 = std::log(2.0 * l_m / (w_m + t_m));
        const double term2 = 0.5;
        const double term3 = 0.2235 * (w_m + t_m) / l_m;

        const double l_henry = (MU_0 / (2.0 * std::numbers::pi)) * l_m * (term1 + term2 + term3);
        return l_henry * 1e9;
    }

    [[nodiscard]] static constexpr double calcMutualInductance(double l_mm, double d_mm) noexcept {
        if (l_mm <= 0.0 || d_mm <= 0.0) return 0.0;
        const double l_m = l_mm * 1e-3;
        const double d_m = d_mm * 1e-3;

        const double ratio = l_m / d_m;
        const double inv_ratio = d_m / l_m;

        const double term1 = std::log(ratio + std::sqrt(1.0 + ratio * ratio));
        const double term2 = std::sqrt(1.0 + inv_ratio * inv_ratio);
        const double term3 = inv_ratio;

        const double m_henry = (MU_0 / (2.0 * std::numbers::pi)) * l_m * (term1 - term2 + term3);
        return m_henry * 1e9;
    }

    [[nodiscard]] static double calcViaArrayInductance(const ViaArrayParams& v) noexcept {
        if (v.count <= 0 || v.board_thickness_mm <= 0.0 || v.drill_diameter_mm <= 0.0) return 0.0;

        const double h_m = v.board_thickness_mm * 1e-3;
        const double d_m = v.drill_diameter_mm * 1e-3;

        const double l_single_h = (MU_0 / (2.0 * std::numbers::pi)) * h_m * (std::log(4.0 * h_m / d_m) - 0.75);
        const double l_single_nh = l_single_h * 1e9;

        if (v.count == 1) return l_single_nh;

        const double s_m = (v.pitch_mm > 0.0) ? (v.pitch_mm * 1e-3) : (d_m * 2.0);
        const double m_h = (MU_0 / (2.0 * std::numbers::pi)) * h_m * (std::log((h_m / s_m) + std::sqrt(1.0 + (h_m * h_m) / (s_m * s_m))) - std::sqrt(1.0 + (s_m * s_m) / (h_m * h_m)) + (s_m / h_m));
        const double m_nh = m_h * 1e9;

        const double n = static_cast<double>(v.count);
        const double l_eff = (1.0 / n) * l_single_nh + ((n - 1.0) / n) * m_nh;
        return std::max(l_eff, 0.05);
    }

    [[nodiscard]] static std::pair<double, double> simulateTransientRK4(double v_in, double i_init, double l_loop_nh, double c_oss_pf, double r_loop_ohm) noexcept {
        const double l_h = l_loop_nh * 1e-9;
        const double c_f = c_oss_pf * 1e-12;

        if (l_h <= 0.0 || c_f <= 0.0) return {v_in, 0.0};

        constexpr double dt = 1e-12;
        constexpr double t_end = 50e-9;

        double i = i_init;
        double v = 0.0;
        double v_max = v_in;

        double t_first_peak = 0.0;
        double t_second_peak = 0.0;
        int peak_count = 0;
        double prev_v = 0.0;
        bool rising = true;

        for (double t = 0.0; t < t_end; t += dt) {
            auto derivatives = [&](double curr_i, double curr_v) -> std::pair<double, double> {
                return {
                    (v_in - curr_v - r_loop_ohm * curr_i) / l_h,
                    curr_i / c_f
                };
            };

            const auto [di1, dv1] = derivatives(i, v);
            const auto [di2, dv2] = derivatives(i + 0.5 * dt * di1, v + 0.5 * dt * dv1);
            const auto [di3, dv3] = derivatives(i + 0.5 * dt * di2, v + 0.5 * dt * dv2);
            const auto [di4, dv4] = derivatives(i + dt * di3, v + dt * dv3);

            i += (dt / 6.0) * (di1 + 2.0 * di2 + 2.0 * di3 + di4);
            v += (dt / 6.0) * (dv1 + 2.0 * dv2 + 2.0 * dv3 + dv4);

            if (v > v_max) v_max = v;

            if (rising && v < prev_v && t > 1e-10) {
                rising = false;
                if (peak_count == 0) {
                    t_first_peak = t;
                    peak_count++;
                } else if (peak_count == 1) {
                    t_second_peak = t;
                    peak_count++;
                }
            } else if (!rising && v > prev_v) {
                rising = true;
            }
            prev_v = v;
        }

        double f_ring_mhz = 0.0;
        if (peak_count >= 2 && (t_second_peak - t_first_peak) > 0.0) {
            f_ring_mhz = (1.0 / (t_second_peak - t_first_peak)) / 1e6;
        } else {
            f_ring_mhz = (1.0 / (2.0 * std::numbers::pi * std::sqrt(l_h * c_f))) / 1e6;
        }

        return {v_max, f_ring_mhz};
    }

    [[nodiscard]] static std::expected<SimulationReport, AnalysisError> analyze(const ConverterSetup& cs) noexcept {
        if (cs.top_trace.length_mm <= 0.0 || cs.top_trace.width_mm <= 0.0) {
            return std::unexpected(AnalysisError::InvalidGeometry);
        }
        if (cs.c_oss_pf <= 0.0) {
            return std::unexpected(AnalysisError::InvalidCapacitance);
        }

        SimulationReport rep;
        const double t_mm = cs.top_trace.thickness_um * 1e-3;

        rep.l_trace_nh = calcPartialSelfInductance(cs.top_trace.length_mm, cs.top_trace.width_mm, t_mm);
        rep.m_gnd_nh = calcMutualInductance(cs.top_trace.length_mm, cs.top_trace.height_gnd_mm);

        const double l_trace_eff = std::max(rep.l_trace_nh - rep.m_gnd_nh, 0.1);
        rep.l_vias_nh = calcViaArrayInductance(cs.vias);

        rep.l_total_loop_nh = l_trace_eff + rep.l_vias_nh + cs.cap_esl_nh + cs.fet_pkg_nh;

        const double di_dt = cs.i_sw / (cs.t_fall_ns * 1e-9);
        rep.v_spike_ideal = (rep.l_total_loop_nh * 1e-9) * di_dt;

        const double r_loop = cs.r_loop_mohm * 1e-3;
        const auto [v_max, f_ring] = simulateTransientRK4(cs.v_in, cs.i_sw, rep.l_total_loop_nh, cs.c_oss_pf, r_loop);
        rep.v_max_transient = v_max;
        rep.f_ringing_mhz = f_ring;

        const double l_h = rep.l_total_loop_nh * 1e-9;
        const double c_f = cs.c_oss_pf * 1e-12;
        rep.r_snub_opt_ohm = std::sqrt(l_h / c_f);
        rep.c_snub_opt_pf = cs.c_oss_pf * 2.5;

        constexpr double f_sw = 1e6;
        const double c_snub_f = rep.c_snub_opt_pf * 1e-12;
        rep.p_snub_watt = c_snub_f * cs.v_in * cs.v_in * f_sw;

        return rep;
    }
};

void displayReport(std::string_view title, const SimulationReport& r) {
    std::cout << "\n===============================================================\n";
    std::cout << "  " << title << "\n";
    std::cout << "===============================================================\n";
    std::cout << std::format("  1. ЕКСТРАКЦІЯ ПАРАЗИТНИХ ІНДУКТИВНОСТЕЙ:\n");
    std::cout << std::format("     - Власна індуктивність L1:                {:6.2f} нГн\n", r.l_trace_nh);
    std::cout << std::format("     - Взаємна індуктивність L2 GND:           {:6.2f} нГн\n", r.m_gnd_nh);
    std::cout << std::format("     - Індуктивність масиву Vias:              {:6.2f} нГн\n", r.l_vias_nh);
    std::cout << std::format("     ----------------------------------------------------------\n");
    std::cout << std::format("     -> ПОВНА ІНДУКТИВНІСТЬ ГАРЯЧОЇ ПЕТЛІ:     {:6.2f} нГн\n\n", r.l_total_loop_nh);

    std::cout << std::format("  2. ПЕРЕХІДНІ ПРОЦЕСИ (RK4 SOLVER):\n");
    std::cout << std::format("     - Ідеальний викид Фарадея (L*di/dt):      {:6.2f} В\n", r.v_spike_ideal);
    std::cout << std::format("     - Пікова перенапруга на стоці:            {:6.2f} В\n", r.v_max_transient);
    std::cout << std::format("     - Частота дзвону:                         {:6.1f} МГц\n\n", r.f_ringing_mhz);

    std::cout << std::format("  3. ПАРАМЕТРИ RC-СНАБЕРА:\n");
    std::cout << std::format("     - Резистор снабера (R_snub):              {:6.2f} Ом\n", r.r_snub_opt_ohm);
    std::cout << std::format("     - Ємність снабера (C_snub):               {:6.1f} пФ\n", r.c_snub_opt_pf);
    std::cout << std::format("     - Розсіювана потужність на 1 МГц:         {:6.3f} Вт\n", r.p_snub_watt);
    std::cout << "===============================================================\n";
}

} // namespace power_pcb

int main() {
    using namespace power_pcb;

    // Конфігурація 1: 2-шарова плата без суцільної землі
    constexpr ConverterSetup bad_setup{
        .v_in = 24.0,
        .i_sw = 15.0,
        .t_fall_ns = 2.0,
        .top_trace = { .length_mm = 15.0, .width_mm = 1.0, .thickness_um = 35.0, .height_gnd_mm = 1.5 },
        .vias = { .board_thickness_mm = 1.6, .drill_diameter_mm = 0.3, .count = 1, .pitch_mm = 0.0 },
        .cap_esl_nh = 0.9,
        .fet_pkg_nh = 2.5,
        .c_oss_pf = 400.0,
        .r_loop_mohm = 25.0
    };

    if (auto res = HotLoopSolver::analyze(bad_setup); res.has_value()) {
        displayReport("НЕВДАЛЕ КОМПОНУВАННЯ (2 ШАРИ, РОЗІРВАНА ЗЕМЛЯ)", *res);
    }

    // Конфігурація 2: 4-шарова плата з суцільною землею L2 (prepreg 0.1 мм)
    constexpr ConverterSetup good_setup{
        .v_in = 24.0,
        .i_sw = 15.0,
        .t_fall_ns = 2.0,
        .top_trace = { .length_mm = 4.0, .width_mm = 3.0, .thickness_um = 35.0, .height_gnd_mm = 0.1 },
        .vias = { .board_thickness_mm = 1.6, .drill_diameter_mm = 0.3, .count = 4, .pitch_mm = 1.0 },
        .cap_esl_nh = 0.35,
        .fet_pkg_nh = 0.4,
        .c_oss_pf = 400.0,
        .r_loop_mohm = 8.0
    };

    if (auto res = HotLoopSolver::analyze(good_setup); res.has_value()) {
        displayReport("ОПТИМАЛЬНЕ КОМПОНУВАННЯ (4 ШАРИ, ПІД КЛЮЧАМИ ЗЕМЛЯ L2)", *res);
    }

    return 0;
}
