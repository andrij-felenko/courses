#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <string_view>
#include <iomanip>
#include <algorithm>
#include <span>

struct DecouplingGroup {
    double capacitance_f{0.0};
    double esr_ohm{0.0};
    double esl_h{0.0};
    int count{1};
    std::string_view label{};

    [[nodiscard]] std::complex<double> impedance_at(double freq_hz) const noexcept {
        if (count <= 0 || freq_hz <= 0.0) {
            return {1e9, 0.0};
        }
        const double w = 2.0 * std::numbers::pi * freq_hz;
        const double r_eq = esr_ohm / count;
        const double l_eq = esl_h / count;
        const double c_eq = capacitance_f * count;
        
        const double x_l = w * l_eq;
        const double x_c = 1.0 / (w * c_eq);
        return {r_eq, x_l - x_c};
    }
};

struct PdnSpecification {
    double v_dd{0.85};
    double ripple_ratio{0.03};
    double i_transient{20.0};

    [[nodiscard]] constexpr double target_impedance() const noexcept {
        return (v_dd * ripple_ratio) / i_transient;
    }
};

class PdnNetworkAnalyzer {
public:
    PdnNetworkAnalyzer(double vrm_r, double vrm_l, std::vector<DecouplingGroup> groups)
        : vrm_resistance_{vrm_r}, vrm_inductance_{vrm_l}, groups_{std::move(groups)} {}

    [[nodiscard]] std::complex<double> calculate_impedance(double freq_hz) const noexcept {
        const double w = 2.0 * std::numbers::pi * freq_hz;
        const std::complex<double> z_vrm{vrm_resistance_, w * vrm_inductance_};
        std::complex<double> y_total = 1.0 / z_vrm;

        for (const auto& group : groups_) {
            y_total += 1.0 / group.impedance_at(freq_hz);
        }
        return 1.0 / y_total;
    }

    struct SweepResult {
        double frequency_hz;
        double magnitude_z;
        double phase_deg;
        bool exceeds_target;
    };

    [[nodiscard]] std::vector<SweepResult> sweep(double f_start, double f_stop,
                                                  int points_per_decade, double z_target) const {
        std::vector<SweepResult> results;
        const double step_factor = std::pow(10.0, 1.0 / points_per_decade);

        for (double f = f_start; f <= f_stop; f *= step_factor) {
            const auto z = calculate_impedance(f);
            const double mag = std::abs(z);
            const double phase = std::arg(z) * 180.0 / std::numbers::pi;
            results.push_back({f, mag, phase, mag > z_target});
        }
        return results;
    }

private:
    double vrm_resistance_{0.0006};
    double vrm_inductance_{2.5e-9};
    std::vector<DecouplingGroup> groups_;
};

int main() {
    const PdnSpecification spec{.v_dd = 0.85, .ripple_ratio = 0.03, .i_transient = 20.0};
    const double z_target = spec.target_impedance();

    std::vector<DecouplingGroup> groups = {
        {.capacitance_f = 470e-6, .esr_ohm = 0.005, .esl_h = 1.5e-9, .count = 4,  .label = "4x 470uF Bulk Tantalum"},
        {.capacitance_f = 22e-6,  .esr_ohm = 0.006, .esl_h = 0.8e-9, .count = 10, .label = "10x 22uF 0805 MLCC"},
        {.capacitance_f = 1.0e-6, .esr_ohm = 0.010, .esl_h = 0.5e-9, .count = 20, .label = "20x 1.0uF 0402 MLCC"},
        {.capacitance_f = 0.1e-6, .esr_ohm = 0.020, .esl_h = 0.4e-9, .count = 40, .label = "40x 0.1uF 0201 MLCC"}
    };

    const PdnNetworkAnalyzer analyzer(0.0006, 2.5e-9, std::move(groups));
    const auto sweep_data = analyzer.sweep(1e3, 1e8, 5, z_target);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== C++20 PDN Network Impedance Sweep ===
";
    std::cout << "Z_target = " << z_target * 1000.0 << " mOhm

";

    double max_z = 0.0;
    double max_f = 0.0;

    for (const auto& pt : sweep_data) {
        if (pt.magnitude_z > max_z) {
            max_z = pt.magnitude_z;
            max_f = pt.frequency_hz;
        }
        std::cout << "f = " << std::setw(11) << pt.frequency_hz << " Hz | "
                  << "|Z| = " << std::setw(8) << pt.magnitude_z * 1000.0 << " mOhm | "
                  << "Phase = " << std::setw(6) << pt.phase_deg << " deg"
                  << (pt.exceeds_target ? " [ALERT: > Z_target]" : "") << "
";
    }

    std::cout << "
Результати перевірки:
";
    std::cout << "Пік імпедансу: " << max_z * 1000.0 << " мОм на " << max_f / 1e6 << " МГц
";
    return 0;
}
