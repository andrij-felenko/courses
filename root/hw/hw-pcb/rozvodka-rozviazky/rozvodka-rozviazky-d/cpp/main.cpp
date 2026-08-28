#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <expected>

namespace pdn {

constexpr double SPEED_OF_LIGHT = 299792458.0;

struct TargetSpecification {
    double nominal_voltage_v{0.90};
    double ripple_tolerance_ratio{0.03};
    double transient_current_a{20.0};

    [[nodiscard]] constexpr double target_impedance() const noexcept {
        return (nominal_voltage_v * ripple_tolerance_ratio) / transient_current_a;
    }
};

struct CapacitorConfig {
    std::string name;
    double capacitance_f{100e-9};
    double esr_ohms{0.018};
    double total_mount_inductance_h{0.78e-9};

    [[nodiscard]] double series_resonant_frequency() const noexcept {
        if (capacitance_f <= 0.0 || total_mount_inductance_h <= 0.0) return 0.0;
        return 1.0 / (2.0 * std::numbers::pi * std::sqrt(capacitance_f * total_mount_inductance_h));
    }
};

class PdnSynthesisEngine {
public:
    static double calculate_antiresonance(double c_small_f, double l_large_h) noexcept {
        if (c_small_f <= 0.0 || l_large_h <= 0.0) return 0.0;
        return 1.0 / (2.0 * std::numbers::pi * std::sqrt(c_small_f * l_large_h));
    }

    static double calculate_effective_radius(double frequency_hz, double dielectric_er, double safety_factor = 4.0) noexcept {
        if (frequency_hz <= 0.0 || dielectric_er <= 1.0) return 0.0;
        const double v_prop = SPEED_OF_LIGHT / std::sqrt(dielectric_er);
        return v_prop / (2.0 * std::numbers::pi * frequency_hz * safety_factor);
    }
};

} // namespace pdn

int main() {
    using namespace pdn;

    constexpr TargetSpecification target_spec{
        .nominal_voltage_v = 0.90,
        .ripple_tolerance_ratio = 0.03,
        .transient_current_a = 20.0
    };

    std::cout << "====================================================================\n"
              << "  C++20 МОДЕЛЮВАННЯ ЦІЛЬОВОГО ІМПЕДАНСУ PDN ТА ТОПОЛОГІЙ\n"
              << "====================================================================\n"
              << "  Номінальна напруга:     " << std::fixed << std::setprecision(2)
              << target_spec.nominal_voltage_v << " В (допуск ±"
              << target_spec.ripple_tolerance_ratio * 100.0 << "%, dV = "
              << target_spec.nominal_voltage_v * target_spec.ripple_tolerance_ratio * 1000.0 << " мВ)\n"
              << "  Стрибок струму:         " << target_spec.transient_current_a << " А\n"
              << "  Цільовий опір PDN:      " << std::setprecision(3)
              << target_spec.target_impedance() * 1000.0 << " мОм (Z_target)\n\n";

    const std::vector<CapacitorConfig> configs = {
        {"0402 100nF (Far Traces)", 100e-9, 0.018, 3.08e-9},
        {"0402 100nF (Side Vias)", 100e-9, 0.018, 0.78e-9},
        {"0201 100nF (VIPPO Bottom)", 100e-9, 0.022, 0.42e-9}
    };

    std::cout << std::left << std::setw(29) << "Топологія монтажу" << " | "
              << std::right << std::setw(10) << "L_mount" << " | "
              << std::setw(12) << "SRF (Резонанс)" << "\n";
    std::cout << "------------------------------+------------+-------------\n";

    for (const auto& cfg : configs) {
        std::cout << std::left << std::setw(29) << cfg.name << " | "
                  << std::right << std::fixed << std::setprecision(2)
                  << std::setw(6) << cfg.total_mount_inductance_h * 1e9 << " нГн  | "
                  << std::setprecision(1) << std::setw(7) << cfg.series_resonant_frequency() / 1e6 << " МГц\n";
    }

    const double f_anti = PdnSynthesisEngine::calculate_antiresonance(10e-9, configs[1].total_mount_inductance_h);
    const double r_eff_100 = PdnSynthesisEngine::calculate_effective_radius(100e6, 4.2);
    const double r_eff_1g = PdnSynthesisEngine::calculate_effective_radius(1e9, 4.2);

    std::cout << "\n  Паразитний антирезонанс (100нФ Side-Via паралельно з 10нФ): "
              << std::fixed << std::setprecision(1) << f_anti / 1e6 << " МГц\n"
              << "  Радіус ефективної дії конденсатора (FR-4, Er=4.2):\n"
              << "    • f = 100 МГц -> r_eff = " << r_eff_100 * 1000.0 << " мм\n"
              << "    • f = 1.0 ГГц -> r_eff = " << r_eff_1g * 1000.0 << " мм\n"
              << "====================================================================\n";

    return 0;
}
