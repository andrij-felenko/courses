#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <string_view>
#include <string>
#include <iomanip>
#include <algorithm>
#include <format>
#include <span>

namespace pdn {

struct Specification {
    double v_dd{0.85};
    double ripple_ratio{0.03};
    double i_transient{20.0};
    double t_rise{400e-12};

    [[nodiscard]] constexpr double target_impedance() const noexcept {
        return (v_dd * ripple_ratio) / i_transient;
    }

    [[nodiscard]] constexpr double knee_frequency() const noexcept {
        return 0.35 / t_rise;
    }
};

struct DecouplingGroup {
    double nominal_cap{1.0e-6};
    double esr_nominal{0.005};
    double esl_nominal{0.35e-9};
    double l_mount{0.18e-9};
    double r_mount{0.0003};
    double v_sat{3.5};
    double bias_alpha{1.2};
    double tan_delta{0.018};
    int    count{1};
    std::string label{"MLCC Group"};

    [[nodiscard]] double derated_capacitance(double v_dc) const noexcept {
        if (v_sat <= 0.0 || v_dc <= 0.0) return nominal_cap;
        const double norm_v = v_dc / v_sat;
        return nominal_cap / std::pow(1.0 + norm_v * norm_v, bias_alpha);
    }

    [[nodiscard]] std::complex<double> impedance_at(double v_dc, double freq_hz) const noexcept {
        if (count <= 0 || freq_hz <= 0.0) return {1e9, 0.0};
        const double w = 2.0 * std::numbers::pi * freq_hz;
        const double c_eff = derated_capacitance(v_dc);
        const double tan_d = tan_delta + 0.008 * std::log10(std::max(freq_hz, 1000.0) / 1000.0);
        const double r_diel = tan_d / (w * c_eff);
        
        const double r_eq = (esr_nominal + r_diel + r_mount) / count;
        const double l_eq = (esl_nominal + l_mount) / count;
        const double c_eq = c_eff * count;
        
        return {r_eq, w * l_eq - 1.0 / (w * c_eq)};
    }
};

struct PlaneCavity {
    double length_a{0.120};
    double width_b{0.090};
    double thickness_d{50e-6};
    double eps_r{4.1};
    double tan_delta{0.018};
    double port_x{0.060};
    double port_y{0.045};
    int    max_modes_m{8};
    int    max_modes_n{8};
    bool   enabled{true};

    [[nodiscard]] std::complex<double> impedance_at(double freq_hz) const noexcept {
        if (!enabled || length_a <= 0.0 || width_b <= 0.0 || thickness_d <= 0.0) return {1e9, 0.0};
        constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;
        constexpr double eps_0 = 8.8541878128e-12;
        constexpr double sigma_cu = 5.8e7;
        const double w = 2.0 * std::numbers::pi * freq_hz;
        
        const double delta_s = std::sqrt(2.0 / (w * mu_0 * sigma_cu));
        const std::complex<double> k = w * std::sqrt(mu_0 * eps_0 * eps_r) * 
            (1.0 - std::complex<double>{0.0, 0.5 * (tan_delta + delta_s / thickness_d)});
        const std::complex<double> k_sq = k * k;

        std::complex<double> sum{0.0, 0.0};
        for (int m = 0; m <= max_modes_m; ++m) {
            const double eps_m = (m == 0) ? 1.0 : std::numbers::sqrt2;
            const double kx = static_cast<double>(m) * std::numbers::pi / length_a;
            const double cos_x = std::cos(kx * port_x);

            for (int n = 0; n <= max_modes_n; ++n) {
                const double eps_n = (n == 0) ? 1.0 : std::numbers::sqrt2;
                const double ky = static_cast<double>(n) * std::numbers::pi / width_b;
                const double cos_y = std::cos(ky * port_y);

                const double k_mn_sq = kx * kx + ky * ky;
                const double c_term = eps_m * eps_m * eps_n * eps_n * cos_x * cos_x * cos_y * cos_y;
                sum += c_term / (k_mn_sq - k_sq);
            }
        }
        const std::complex<double> coeff{0.0, w * mu_0 * thickness_d / (length_a * width_b)};
        return coeff * sum;
    }
};

struct VrmModel {
    double r_dc{0.0005};
    double l_out{0.35e-9};
    double a_0{1000.0};
    double f_z1{25e3};
    double f_z2{40e3};
    double f_p1{300e3};
    double f_p2{1.5e6};
    bool   avp_enabled{true};
    double r_droop{0.001275};

    [[nodiscard]] std::complex<double> impedance_at(double freq_hz, double target_z) const noexcept {
        const double w = 2.0 * std::numbers::pi * freq_hz;
        const std::complex<double> s{0.0, w};
        const std::complex<double> z_open{r_dc, w * l_out};

        const std::complex<double> num = a_0 * (1.0 + s / (2.0 * std::numbers::pi * f_z1)) * 
                                               (1.0 + s / (2.0 * std::numbers::pi * f_z2));
        const std::complex<double> den = s * (1.0 + s / (2.0 * std::numbers::pi * f_p1)) * 
                                             (1.0 + s / (2.0 * std::numbers::pi * f_p2));
        const std::complex<double> t_loop = num / den;

        if (avp_enabled) {
            const double r_d = (r_droop > 0.0) ? r_droop : target_z;
            return std::complex<double>{r_d, 0.0} + (z_open - std::complex<double>{r_d, 0.0}) / (1.0 + t_loop);
        }
        return z_open / (1.0 + t_loop);
    }
};

struct DiePackageModel {
    double c_die{150e-9};
    double r_die{0.05};
    double l_pkg{0.08e-9};
    double r_pkg{0.0003};
};

struct ResonantPeak {
    double freq_hz{0.0};
    double magnitude_z{0.0};
    double q_factor{1.0};
    double margin_db{0.0};
    bool   is_violation{false};
};

class Analyzer {
public:
    Analyzer(Specification spec, std::vector<DecouplingGroup> groups,
             VrmModel vrm, PlaneCavity plane, DiePackageModel die_pkg)
        : spec_{spec}, groups_{std::move(groups)}, vrm_{vrm},
          plane_{plane}, die_pkg_{die_pkg} {}

    [[nodiscard]] std::complex<double> calculate_impedance(double freq_hz) const noexcept {
        const auto z_vrm = vrm_.impedance_at(freq_hz, spec_.target_impedance());
        std::complex<double> y_pcb = 1.0 / z_vrm;

        for (const auto& group : groups_) {
            y_pcb += 1.0 / group.impedance_at(spec_.v_dd, freq_hz);
        }
        if (plane_.enabled) {
            y_pcb += 1.0 / plane_.impedance_at(freq_hz);
        }
        const auto z_pcb = 1.0 / y_pcb;

        const double w = 2.0 * std::numbers::pi * freq_hz;
        const std::complex<double> z_pkg{die_pkg_.r_pkg, w * die_pkg_.l_pkg};
        const std::complex<double> z_die{die_pkg_.r_die, -1.0 / (w * die_pkg_.c_die)};
        const std::complex<double> z_board_pkg = z_pcb + z_pkg;
        return (z_board_pkg * z_die) / (z_board_pkg + z_die);
    }

    struct SweepPoint {
        double freq_hz;
        double magnitude_z;
        double phase_deg;
    };

    [[nodiscard]] std::vector<SweepPoint> run_sweep(double f_start, double f_stop, int pts_per_dec) const {
        std::vector<SweepPoint> results;
        const double step_factor = std::pow(10.0, 1.0 / pts_per_dec);

        for (double f = f_start; f <= f_stop; f *= step_factor) {
            const auto z = calculate_impedance(f);
            results.push_back({f, std::abs(z), std::arg(z) * 180.0 / std::numbers::pi});
        }
        return results;
    }

    [[nodiscard]] std::vector<ResonantPeak> detect_peaks(std::span<const SweepPoint> sweep_data) const {
        std::vector<ResonantPeak> peaks;
        if (sweep_data.size() < 3) return peaks;

        const double z_target = spec_.target_impedance();

        for (size_t i = 1; i < sweep_data.size() - 1; ++i) {
            if (sweep_data[i].magnitude_z > sweep_data[i - 1].magnitude_z &&
                sweep_data[i].magnitude_z > sweep_data[i + 1].magnitude_z) {
                const double mag = sweep_data[i].magnitude_z;
                const double margin = 20.0 * std::log10(z_target / mag);
                
                const double level_3db = mag / std::numbers::sqrt2;
                double f_low = sweep_data[i - 1].freq_hz;
                double f_high = sweep_data[i + 1].freq_hz;

                for (int k = static_cast<int>(i); k >= 0; --k) {
                    if (sweep_data[k].magnitude_z <= level_3db) { f_low = sweep_data[k].freq_hz; break; }
                }
                for (size_t k = i; k < sweep_data.size(); ++k) {
                    if (sweep_data[k].magnitude_z <= level_3db) { f_high = sweep_data[k].freq_hz; break; }
                }
                const double bw = f_high - f_low;
                const double q = (bw > 0.0) ? (sweep_data[i].freq_hz / bw) : 1.0;

                peaks.push_back({sweep_data[i].freq_hz, mag, q, margin, mag > z_target});
            }
        }
        return peaks;
    }

private:
    Specification spec_;
    std::vector<DecouplingGroup> groups_;
    VrmModel vrm_;
    PlaneCavity plane_;
    DiePackageModel die_pkg_;
};

} // namespace pdn

int main() {
    const pdn::Specification spec{
        .v_dd = 0.85,
        .ripple_ratio = 0.03,
        .i_transient = 20.0,
        .t_rise = 400e-12
    };

    std::vector<pdn::DecouplingGroup> groups = {
        { .nominal_cap = 470e-6, .esr_nominal = 0.0045, .esl_nominal = 1.2e-9, .l_mount = 0.3e-9, .r_mount = 0.0002, .v_sat = 16.0, .bias_alpha = 0.2, .tan_delta = 0.05, .count = 4,  .label = "4x 470uF Bulk Polymer" },
        { .nominal_cap = 22e-6,  .esr_nominal = 0.0035, .esl_nominal = 0.65e-9, .l_mount = 0.25e-9, .r_mount = 0.0003, .v_sat = 4.0,  .bias_alpha = 1.1, .tan_delta = 0.02, .count = 16, .label = "16x 22uF 0805 X7R" },
        { .nominal_cap = 2.2e-6, .esr_nominal = 0.0050, .esl_nominal = 0.35e-9, .l_mount = 0.18e-9, .r_mount = 0.0004, .v_sat = 3.5,  .bias_alpha = 1.2, .tan_delta = 0.018, .count = 24, .label = "24x 2.2uF 0402 X7R" },
        { .nominal_cap = 0.47e-6,.esr_nominal = 0.0080, .esl_nominal = 0.18e-9, .l_mount = 0.12e-9, .r_mount = 0.0005, .v_sat = 3.0,  .bias_alpha = 1.3, .tan_delta = 0.015, .count = 40, .label = "40x 0.47uF 0306 Rev-Geo" }
    };

    const pdn::VrmModel vrm{
        .r_dc = 0.0005,
        .l_out = 0.35e-9,
        .f_crossover = 120e3,
        .a_0 = 1000.0,
        .f_z1 = 25e3,
        .f_z2 = 40e3,
        .f_p1 = 300e3,
        .f_p2 = 1.5e6,
        .avp_enabled = true,
        .r_droop = spec.target_impedance()
    };

    const pdn::PlaneCavity plane{
        .length_a = 0.120,
        .width_b = 0.090,
        .thickness_d = 50e-6,
        .eps_r = 4.1,
        .tan_delta = 0.018,
        .port_x = 0.060,
        .port_y = 0.045,
        .max_modes_m = 8,
        .max_modes_n = 8,
        .enabled = true
    };

    const pdn::DiePackageModel die_pkg{
        .c_die = 150e-9,
        .r_die = 0.05,
        .l_pkg = 0.08e-9,
        .r_pkg = 0.0003
    };

    const pdn::Analyzer analyzer(spec, std::move(groups), vrm, plane, die_pkg);
    const auto sweep_data = analyzer.run_sweep(10.0, 1.0e9, 10);
    const auto peaks = analyzer.detect_peaks(sweep_data);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=================================================================
";
    std::cout << "        C++20 PDN IMPEDANCE & ANTI-RESONANCE ANALYZER
";
    std::cout << "=================================================================
";
    std::cout << "Z_target = " << spec.target_impedance() * 1000.0 << " mOhm | f_knee = " 
              << spec.knee_frequency() / 1e6 << " MHz

";

    std::cout << "Виявлені антирезонансні піки:
";
    std::cout << "-----------------------------------------------------------------
";
    std::cout << " Частота піку    |Z_peak|      Добротність Q   Запас (дБ)   Вердикт
";
    std::cout << "-----------------------------------------------------------------
";
    
    bool any_violation = false;
    for (const auto& pk : peaks) {
        std::cout << std::setw(9) << pk.freq_hz / 1e6 << " MHz | "
                  << std::setw(7) << pk.magnitude_z * 1000.0 << " mOhm | "
                  << "   Q = " << std::setw(6) << pk.q_factor << "   | "
                  << std::setw(6) << pk.margin_db << " dB | "
                  << (pk.is_violation ? "АВАРІЯ (VIOLATION)" : "В МЕЖАХ ДОПУСКУ") << "
";
        if (pk.is_violation) any_violation = true;
    }
    std::cout << "-----------------------------------------------------------------
";
    std::cout << (any_violation ? "СТАТУС: ПОМИЛКА — Потрібне демпфування піків!
" 
                                : "СТАТУС: УСПІХ — Профіль PDN повністю відповідає Z_target.
");
    return 0;
}
