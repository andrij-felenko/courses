/* Об'єктно-орієнтований інженерний аналізатор механіки тяг на C++20 */
#include <iostream>
#include <iomanip>
#include <numbers>
#include <cmath>
#include <string_view>

namespace flight_mechanics {

struct FlightConditions {
    double air_density_kg_m3{1.225};   // густина повітря на висоті польоту, кг/м3
    double max_speed_mps{41.67};       // розрахункова максимальна швидкість v_ne, м/с
};

struct ControlSurface {
    double span_m{0.45};               // розмах рульової площини, м
    double chord_m{0.055};             // середня хорда площини, м
    double max_deflection_deg{20.0};   // граничний кут відхилення, градуси
    double ch_per_deg{0.0035};         // коефіцієнт dC_h / d_delta на градус
};

struct LinkageSetup {
    double r_servo_mm{15.0};           // радіус качалки сервоприводу, мм
    double r_horn_mm{20.0};            // радіус кабанчика руля, мм
    double rod_length_mm{220.0};       // вільна довжина тяги між шарнірами, мм
    double rod_outer_d_mm{4.0};        // зовнішній діаметр тяги, мм
    double rod_inner_d_mm{2.5};        // внутрішній діаметр (0 для моноліту), мм
    double young_modulus_gpa{130.0};   // модуль Юнга E, ГПа
    double efficiency{0.95};           // механічний ККД наконечників
};

struct AnalysisReport {
    double dynamic_pressure_pa{0.0};
    double hinge_moment_nm{0.0};
    double pushrod_force_n{0.0};
    double euler_buckling_pcr_n{0.0};
    double buckling_margin{0.0};
    double req_servo_torque_nm{0.0};
    double req_servo_torque_kgcm{0.0};

    [[nodiscard]] constexpr bool is_buckling_safe() const noexcept {
        return buckling_margin >= 2.0;
    }
};

class LinkageAnalyzer {
public:
    [[nodiscard]] static AnalysisReport compute(
        const FlightConditions& flight,
        const ControlSurface& surface,
        const LinkageSetup& linkage,
        double safety_factor = 2.2) noexcept
    {
        AnalysisReport report;

        // 1. Динамічний напір q = 0.5 * rho * v^2
        report.dynamic_pressure_pa = 0.5 * flight.air_density_kg_m3 * 
                                     flight.max_speed_mps * flight.max_speed_mps;

        // 2. Площа руля S = span * chord
        const double area = surface.span_m * surface.chord_m;

        // 3. Коефіцієнт шарнірного моменту C_h
        const double c_h = surface.ch_per_deg * surface.max_deflection_deg;

        // 4. Шарнірний момент M_h = q * S * chord * C_h
        report.hinge_moment_nm = report.dynamic_pressure_pa * area * surface.chord_m * c_h;

        // 5. Сила в тязі F_rod = M_h / (r_horn * eta)
        const double r_horn_m = linkage.r_horn_mm * 1e-3;
        report.pushrod_force_n = report.hinge_moment_nm / (r_horn_m * linkage.efficiency);

        // 6. Момент інерції поперечного перерізу I = pi * (D^4 - d^4) / 64
        const double D_m = linkage.rod_outer_d_mm * 1e-3;
        const double d_m = linkage.rod_inner_d_mm * 1e-3;
        const double i_moment = (std::numbers::pi * (std::pow(D_m, 4.0) - std::pow(d_m, 4.0))) / 64.0;

        // 7. Критична сила стійкості Ейлера P_cr = (pi^2 * E * I) / L^2
        const double L_m = linkage.rod_length_mm * 1e-3;
        const double E_pa = linkage.young_modulus_gpa * 1e9;
        report.euler_buckling_pcr_n = (std::numbers::pi * std::numbers::pi * E_pa * i_moment) / (L_m * L_m);

        // 8. Коефіцієнт запасу стійкості
        report.buckling_margin = (report.pushrod_force_n > 1e-6)
                                 ? (report.euler_buckling_pcr_n / report.pushrod_force_n)
                                 : 999.0;

        // 9. Потрібний момент на валу сервоприводу
        const double r_servo_m = linkage.r_servo_mm * 1e-3;
        report.req_servo_torque_nm = (report.hinge_moment_nm / linkage.efficiency) * 
                                     (r_servo_m / r_horn_m) * safety_factor;

        // Переведення в кг·см (1 Н·м = 10.19716 кг·см)
        report.req_servo_torque_kgcm = report.req_servo_torque_nm * 10.19716;

        return report;
    }

    static void print_report(std::string_view title, const AnalysisReport& rep) {
        std::cout << "\n--- [" << title << "] ---\n"
                  << "  Осьове зусилля в тязі:          " << std::fixed << std::setprecision(2) 
                  << rep.pushrod_force_n << " Н\n"
                  << "  Критична сила Ейлера (P_cr):    " << rep.euler_buckling_pcr_n << " Н\n"
                  << "  Запас стійкості на поздовжній вигин: " << rep.buckling_margin 
                  << (rep.is_buckling_safe() ? " (СТІЙКО)" : " (НЕБЕЗПЕКА: ВТРАТА СТІЙКОСТІ!)") << "\n"
                  << "  Потрібний момент сервоприводу:  " << rep.req_servo_torque_kgcm 
                  << " кг·см (" << rep.req_servo_torque_nm << " Н·м)\n";
    }
};

} // namespace flight_mechanics

int main() {
    using namespace flight_mechanics;

    const FlightConditions flight{
        .air_density_kg_m3 = 1.225,
        .max_speed_mps = 41.67         // 150 км/год
    };

    const ControlSurface aileron{
        .span_m = 0.45,
        .chord_m = 0.055,
        .max_deflection_deg = 20.0,
        .ch_per_deg = 0.0035
    };

    // Сталевий пруток 1.2 мм
    const LinkageSetup steel_wire{
        .r_servo_mm = 15.0,
        .r_horn_mm = 20.0,
        .rod_length_mm = 220.0,
        .rod_outer_d_mm = 1.2,
        .rod_inner_d_mm = 0.0,
        .young_modulus_gpa = 210.0,
        .efficiency = 0.92
    };

    // Карбонова трубка 4.0 / 2.5 мм
    const LinkageSetup carbon_tube{
        .r_servo_mm = 15.0,
        .r_horn_mm = 20.0,
        .rod_length_mm = 220.0,
        .rod_outer_d_mm = 4.0,
        .rod_inner_d_mm = 2.5,
        .young_modulus_gpa = 130.0,
        .efficiency = 0.95
    };

    const auto rep_steel = LinkageAnalyzer::compute(flight, aileron, steel_wire, 2.2);
    const auto rep_carbon = LinkageAnalyzer::compute(flight, aileron, carbon_tube, 2.2);

    std::cout << "=== ІНЖЕНЕРНИЙ АНАЛІЗ РУЛЬОВОГО ПРИВОДУ БПЛА ===\n"
              << "Динамічний напір q: " << std::fixed << std::setprecision(1) 
              << rep_steel.dynamic_pressure_pa << " Па\n"
              << "Шарнірний аеродинамічний момент M_h: " << std::setprecision(4) 
              << rep_steel.hinge_moment_nm << " Н·м\n";

    LinkageAnalyzer::print_report("Сталевий дріт d=1.2 мм", rep_steel);
    LinkageAnalyzer::print_report("Карбонова трубка D=4.0 мм, d=2.5 мм", rep_carbon);

    return 0;
}
