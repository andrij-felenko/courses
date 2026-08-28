/*
 * mounting_mechanics.hpp / .cpp — об'єктно-орієнтований аналізатор кріплення (C++20).
 */

#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <format>

namespace pcb::mechanics {

constexpr double Ipc9704SafeMicrostrainThreshold = 500.0;

struct MountingParameters {
    double screw_diameter_mm{3.0};
    double washer_diameter_mm{7.0};
    double nut_friction_factor{0.20};
    double tightening_torque_nm{0.60};
    double pcb_thickness_mm{1.60};
    double span_between_standoffs_mm{60.0};
    double standoff_height_mismatch_mm{0.25};
};

struct CalculationReport {
    double clamping_force_n{0.0};
    double washer_pressure_mpa{0.0};
    double peak_microstrain{0.0};
    double recommended_keepout_radius_mm{0.0};
    bool is_ipc9704_compliant{false};

    [[nodiscard]] constexpr std::string_view status_string() const noexcept {
        return is_ipc9704_compliant ? "БЕЗПЕЧНО" : "НЕБЕЗПЕЧНО: РИЗИК ЗЛАМУ MLCC";
    }
};

class MountingNodeEvaluator {
public:
    [[nodiscard]] static constexpr CalculationReport evaluate(const MountingParameters& p) noexcept {
        CalculationReport report{};

        // 1. Осьове зусилля: F = T / (K * d)
        const double d_meters = p.screw_diameter_mm * 1e-3;
        report.clamping_force_n = p.tightening_torque_nm / (p.nut_friction_factor * d_meters);

        // 2. Тиск під шайбою
        const double hole_d = p.screw_diameter_mm + 0.2;
        const double contact_area_mm2 = (std::numbers::pi / 4.0) * 
            (std::pow(p.washer_diameter_mm, 2) - std::pow(hole_d, 2));
        report.washer_pressure_mpa = report.clamping_force_n / contact_area_mm2;

        // 3. Деформація розтягу плати: ε = (6 * t * Δh) / L^2
        const double t_m = p.pcb_thickness_mm * 1e-3;
        const double dh_m = p.standoff_height_mismatch_mm * 1e-3;
        const double l_m = p.span_between_standoffs_mm * 1e-3;

        const double strain_unitless = (6.0 * t_m * dh_m) / (l_m * l_m);
        report.peak_microstrain = strain_unitless * 1e6;

        // 4. Радіус заборони SMD
        report.recommended_keepout_radius_mm = (p.washer_diameter_mm / 2.0) + 1.25;

        // 5. Відповідність IPC-9704
        report.is_ipc9704_compliant = (report.peak_microstrain <= Ipc9704SafeMicrostrainThreshold);

        return report;
    }
};

} // namespace pcb::mechanics

int main() {
    using namespace pcb::mechanics;

    constexpr MountingParameters config{
        .screw_diameter_mm = 3.0,
        .washer_diameter_mm = 7.0,
        .nut_friction_factor = 0.20,
        .tightening_torque_nm = 0.60,
        .pcb_thickness_mm = 1.60,
        .span_between_standoffs_mm = 60.0,
        .standoff_height_mismatch_mm = 0.25
    };

    constexpr auto report = MountingNodeEvaluator::evaluate(config);

    std::cout << "=== АНАЛІЗ КРІПИЛЬНОГО ВУЗЛА M3 (C++20) ===\n";
    std::cout << std::format("Осьове зусилля стискання F_clamp:   {:.1f} Н\n", report.clamping_force_n);
    std::cout << std::format("Контактний тиск під шайбою:       {:.2f} МПа\n", report.washer_pressure_mpa);
    std::cout << std::format("Поверхнева деформація текстоліту: {:.1f} με\n", report.peak_microstrain);
    std::cout << std::format("Радіус зони заборони SMD (Keepout): {:.2f} мм\n", report.recommended_keepout_radius_mm);
    std::cout << std::format("Статус IPC/JEDEC-9704 (<=500 με):  {}\n", report.status_string());

    return 0;
}
